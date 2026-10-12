r"""Conversor de JSON a CSV con estrategia de filtro.

Lee un documento JSON desde un archivo (``-i``) o desde la entrada estándar y
escribe el CSV resultante en un archivo (``-o``) o en la salida estándar.

Uso::

    python json2csv.py [-i ENTRADA] [-o SALIDA] [-d DELIMITADOR]

Reglas de conversión:

* Una lista de objetos produce una fila por objeto.
* Un objeto produce una única fila.
* Los objetos anidados se aplanan con claves ``a.b``.
* Las listas se guardan como JSON dentro de una única celda.
* Los elementos de una lista que no son objetos van a la columna ``value``.

Códigos de salida:

* 0: conversión correcta.
* 1: JSON inválido o estructura no soportada.
* 2: argumentos inválidos (por ejemplo, un delimitador de más de un carácter).
* 3: error de entrada/salida (archivo inexistente, sin permisos, etc.).
* 130: ejecución interrumpida por el usuario (Ctrl+C).
"""

import argparse
import csv
import io
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, TypeGuard

__version__ = "0.1.0"
__build__ = "1"

DEFAULT_DELIMITER = ","
KEY_SEPARATOR = "."
SCALAR_COLUMN = "value"

EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_ARGS_ERROR = 2
EXIT_IO_ERROR = 3
EXIT_INTERRUPTED = 130


class Json2CsvError(Exception):
    """Error base de la herramienta, con su código de salida asociado."""

    exit_code: int = EXIT_DATA_ERROR


class DelimiterError(Json2CsvError):
    """El delimitador indicado no es válido."""

    exit_code = EXIT_ARGS_ERROR


class JsonFormatError(Json2CsvError):
    """El texto de entrada no es JSON válido o no puede convertirse a CSV."""

    exit_code = EXIT_DATA_ERROR


class InputOutputError(Json2CsvError):
    """Falló la lectura de la entrada o la escritura de la salida."""

    exit_code = EXIT_IO_ERROR


def parse_delimiter(raw: str) -> str:
    r"""Valida y normaliza el delimitador recibido por línea de comandos.

    Se acepta ``\t`` (barra invertida y t) como alias de la tabulación.

    Args:
        raw: Delimitador tal como lo escribió el usuario.

    Returns:
        El delimitador, de exactamente un carácter.

    Raises:
        DelimiterError: Si no es de un solo carácter o no es utilizable en CSV.
    """
    delimiter = "\t" if raw == "\\t" else raw
    if len(delimiter) != 1:
        raise DelimiterError(
            f"el delimitador debe ser un único carácter (se recibió {raw!r})"
        )
    if delimiter in {'"', "\r", "\n"}:
        raise DelimiterError(f"el delimitador {delimiter!r} no es válido para CSV")
    return delimiter


def _is_object(value: object) -> TypeGuard[dict[str, Any]]:
    """Indica si el valor es un objeto JSON (diccionario)."""
    return isinstance(value, dict)


def _is_array(value: object) -> TypeGuard[list[Any]]:
    """Indica si el valor es un arreglo JSON (lista)."""
    return isinstance(value, list)


def _to_cell(value: Any) -> str:
    """Convierte un valor JSON en el texto de una celda CSV."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if _is_array(value) or _is_object(value):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def flatten(record: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Aplana un objeto JSON anidado en columnas simples.

    Args:
        record: Objeto JSON ya decodificado.
        prefix: Prefijo de clave usado en la recursión.

    Returns:
        Diccionario de columna a texto de celda.
    """
    flat: dict[str, str] = {}
    for key, value in record.items():
        column = f"{prefix}{key}"
        if _is_object(value) and value:
            flat.update(flatten(value, f"{column}{KEY_SEPARATOR}"))
        else:
            flat[column] = _to_cell(value)
    return flat


def extract_rows(data: Any) -> list[dict[str, str]]:
    """Obtiene las filas planas a partir de un documento JSON decodificado.

    Args:
        data: Resultado de ``json.loads``.

    Returns:
        Una fila (diccionario columna a celda) por cada registro.

    Raises:
        JsonFormatError: Si el documento no es un objeto ni una lista.
    """
    if _is_object(data):
        items: list[Any] = [data]
    elif _is_array(data):
        items = data
    else:
        raise JsonFormatError("el JSON debe ser un objeto o una lista")
    return [
        flatten(item) if _is_object(item) else {SCALAR_COLUMN: _to_cell(item)}
        for item in items
    ]


def convert(text: str, delimiter: str = DEFAULT_DELIMITER) -> str:
    """Convierte un texto JSON en un texto CSV.

    Args:
        text: Documento JSON.
        delimiter: Delimitador de columnas del CSV.

    Returns:
        El CSV con su fila de encabezado, o una cadena vacía si no hay filas.

    Raises:
        DelimiterError: Si el delimitador no es válido.
        JsonFormatError: Si el JSON es inválido o no puede convertirse.
    """
    delimiter = parse_delimiter(delimiter)
    if not text.strip():
        raise JsonFormatError("la entrada está vacía")
    try:
        rows = extract_rows(json.loads(text))
    except json.JSONDecodeError as exc:
        raise JsonFormatError(
            f"JSON inválido (línea {exc.lineno}, columna {exc.colno}): {exc.msg}"
        ) from exc
    except RecursionError as exc:
        raise JsonFormatError(
            "el JSON tiene un anidamiento demasiado profundo"
        ) from exc
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    if not fieldnames:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _use_utf8(stream: object, encoding: str) -> None:
    """Reconfigura una entrada o salida estándar redirigida para usar UTF-8."""
    if isinstance(stream, io.TextIOWrapper) and not stream.isatty():
        stream.reconfigure(encoding=encoding)


def read_input(path: str | None) -> str:
    """Lee el texto de entrada desde un archivo o desde la entrada estándar.

    Args:
        path: Ruta del archivo, o ``None`` para leer de la entrada estándar.

    Returns:
        El texto leído, sin la marca BOM de UTF-8 si la tuviera.

    Raises:
        InputOutputError: Si no se puede leer o no está codificado en UTF-8.
    """
    origin = "la entrada estándar" if path is None else repr(path)
    try:
        if path is None:
            _use_utf8(sys.stdin, "utf-8-sig")
            return sys.stdin.read()
        return Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise InputOutputError(f"no se pudo leer {origin}: {exc}") from exc


def write_output(text: str, path: str | None) -> None:
    """Escribe el texto en un archivo o en la salida estándar.

    Args:
        text: Texto a escribir.
        path: Ruta del archivo, o ``None`` para usar la salida estándar.

    Raises:
        InputOutputError: Si no se puede escribir o no se puede codificar.
    """
    destination = "la salida estándar" if path is None else repr(path)
    try:
        if path is None:
            _use_utf8(sys.stdout, "utf-8")
            sys.stdout.write(text)
            sys.stdout.flush()
        else:
            Path(path).write_bytes(text.encode("utf-8"))
    except (OSError, UnicodeEncodeError) as exc:
        raise InputOutputError(f"no se pudo escribir en {destination}: {exc}") from exc


def _ensure_distinct(input_path: str | None, output_path: str | None) -> None:
    """Evita que la salida sobrescriba el archivo de entrada."""
    if input_path is None or output_path is None:
        return
    if Path(input_path).resolve() == Path(output_path).resolve():
        raise InputOutputError("el archivo de entrada y el de salida son el mismo")


def build_parser() -> argparse.ArgumentParser:
    """Crea el analizador de argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(
        prog="json2csv",
        description="Convierte JSON a CSV. Sin -i lee la entrada estándar y "
        "sin -o escribe en la salida estándar.",
    )
    parser.add_argument("-i", "--input", metavar="ENTRADA", help="archivo JSON")
    parser.add_argument("-o", "--output", metavar="SALIDA", help="archivo CSV")
    parser.add_argument(
        "-d",
        "--delimiter",
        default=DEFAULT_DELIMITER,
        metavar="DELIMITADOR",
        help="delimitador de columnas (por defecto: coma; use \\t para tabulación)",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__} (build {__build__})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada de la herramienta.

    Args:
        argv: Argumentos de línea de comandos; por defecto, ``sys.argv[1:]``.

    Returns:
        Código de salida del proceso (0 si todo salió bien).
    """
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_ARGS_ERROR
    try:
        delimiter = parse_delimiter(args.delimiter)
        _ensure_distinct(args.input, args.output)
        result = convert(read_input(args.input), delimiter)
        write_output(result, args.output)
    except Json2CsvError as exc:
        print(f"json2csv: error: {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("json2csv: interrumpido por el usuario", file=sys.stderr)
        return EXIT_INTERRUPTED
    except Exception as exc:  # noqa: BLE001 - último recurso: nunca mostrar traceback
        print(f"json2csv: error inesperado: {exc!r}", file=sys.stderr)
        return EXIT_DATA_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
