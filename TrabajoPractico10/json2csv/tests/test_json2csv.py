"""Pruebas unitarias de json2csv. Cada docstring enuncia la hipótesis probada."""

import io
import runpy
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from json2csv import __build__, __version__, convert, main
from json2csv import json2csv as module
from json2csv.json2csv import (
    DelimiterError,
    JsonFormatError,
    parse_delimiter,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "json2csv" / "json2csv.py"


def _stdin(monkeypatch: pytest.MonkeyPatch, data: bytes) -> None:
    """Reemplaza la entrada estándar por un flujo con los bytes indicados."""
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))


# --- Conversión -------------------------------------------------------------


def test_list_of_objects_gives_one_row_each() -> None:
    """Hipótesis: una lista de objetos produce encabezado y una fila por objeto."""
    assert convert('[{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]') == "a,b\n1,x\n2,y\n"


def test_single_object_gives_one_row() -> None:
    """Hipótesis: un objeto suelto produce una única fila."""
    assert convert('{"a": 1}') == "a\n1\n"


def test_header_is_union_of_keys_in_order() -> None:
    """Hipótesis: las claves ausentes en una fila quedan como celdas vacías."""
    assert convert('[{"a": 1}, {"b": 2, "a": 3}]') == "a,b\n1,\n3,2\n"


def test_nested_objects_are_flattened() -> None:
    """Hipótesis: los objetos anidados se aplanan con claves separadas por punto."""
    assert convert('{"u": {"n": "Ana", "d": {"c": "UY"}}}') == "u.n,u.d.c\nAna,UY\n"


def test_lists_and_empty_objects_become_json_cells() -> None:
    """Hipótesis: listas y objetos vacíos se guardan como JSON en una celda."""
    assert convert('{"t": [1, "a"], "e": {}}') == 't,e\n"[1,""a""]",{}\n'


def test_null_and_booleans() -> None:
    """Hipótesis: null es una celda vacía y los booleanos se escriben en JSON."""
    assert (
        convert('{"a": null, "b": true, "c": false, "d": 1.5}')
        == "a,b,c,d\n,true,false,1.5\n"
    )


def test_list_of_scalars_uses_value_column() -> None:
    """Hipótesis: los elementos que no son objetos van a la columna value."""
    assert convert('[1, "dos", null]') == 'value\n1\ndos\n""\n'


def test_empty_list_gives_empty_output() -> None:
    """Hipótesis: una lista vacía no produce filas ni encabezado."""
    assert convert("[]") == ""


def test_unicode_is_preserved() -> None:
    """Hipótesis: los caracteres no ASCII se conservan sin escapar."""
    assert convert('[{"n": "José ñandú"}]') == "n\nJosé ñandú\n"


def test_values_with_delimiter_are_quoted() -> None:
    """Hipótesis: un valor que contiene el delimitador se entrecomilla."""
    assert convert('[{"a": "x,y"}]') == 'a\n"x,y"\n'


def test_custom_delimiter_and_tab_alias() -> None:
    """Hipótesis: se respeta el delimitador y barra-t equivale a tabulación."""
    assert convert('[{"a": 1, "b": 2}]', ";") == "a;b\n1;2\n"
    assert convert('[{"a": 1, "b": 2}]', "\\t") == "a\tb\n1\t2\n"


@pytest.mark.parametrize("delimiter", ["", ",,", '"', "\n", "\r"])
def test_invalid_delimiter_is_rejected(delimiter: str) -> None:
    """Hipótesis: un delimitador de longitud distinta de uno o prohibido falla."""
    with pytest.raises(DelimiterError):
        parse_delimiter(delimiter)


@pytest.mark.parametrize("text", ["5", '"hola"', "null"])
def test_top_level_scalar_is_rejected(text: str) -> None:
    """Hipótesis: un JSON cuya raíz no es objeto ni lista se rechaza."""
    with pytest.raises(JsonFormatError):
        convert(text)


def test_invalid_json_reports_position() -> None:
    """Hipótesis: un JSON inválido informa la línea y la columna del error."""
    with pytest.raises(JsonFormatError, match="línea 1, columna"):
        convert("[1, 2")


@pytest.mark.parametrize("text", ["", "   \n"])
def test_empty_input_is_rejected(text: str) -> None:
    """Hipótesis: una entrada vacía o en blanco se rechaza con un error claro."""
    with pytest.raises(JsonFormatError, match="vacía"):
        convert(text)


def test_excessive_nesting_is_rejected() -> None:
    """Hipótesis: un anidamiento excesivo no provoca un traceback sino un error."""
    with pytest.raises(JsonFormatError, match="profundo"):
        convert("[" * 100_000)


# --- Línea de comandos ------------------------------------------------------


def test_main_file_to_file(tmp_path: Path) -> None:
    """Hipótesis: con -i y -o se lee y escribe en archivos y el código es 0."""
    source = tmp_path / "in.json"
    target = tmp_path / "out.csv"
    source.write_text('\ufeff[{"a": 1, "b": "é"}]', encoding="utf-8")
    code = main(["-i", str(source), "-o", str(target), "-d", ";"])
    assert code == 0
    assert target.read_text(encoding="utf-8") == "a;b\n1;é\n"


def test_main_stdin_to_stdout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Hipótesis: sin -i ni -o actúa como filtro entre stdin y stdout."""
    _stdin(monkeypatch, '[{"a": "ñ"}]'.encode())
    assert main([]) == 0
    assert capsys.readouterr().out == "a\nñ\n"


def test_main_stdin_as_plain_text_stream(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Hipótesis: también funciona con una entrada de texto sin búfer binario."""
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"a": 1}'))
    assert main([]) == 0
    assert capsys.readouterr().out == "a\n1\n"


def test_main_missing_input_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Hipótesis: un archivo de entrada inexistente devuelve 3 y un mensaje."""
    assert main(["-i", str(tmp_path / "no_existe.json")]) == 3
    assert "no se pudo leer" in capsys.readouterr().err


def test_main_invalid_json_does_not_create_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Hipótesis: ante un JSON inválido devuelve 1 y no crea el archivo de salida."""
    source = tmp_path / "in.json"
    target = tmp_path / "out.csv"
    source.write_text("{roto", encoding="utf-8")
    assert main(["-i", str(source), "-o", str(target)]) == 1
    assert not target.exists()
    assert "JSON inválido" in capsys.readouterr().err


def test_main_invalid_delimiter(capsys: pytest.CaptureFixture[str]) -> None:
    """Hipótesis: un delimitador inválido devuelve 2 antes de leer la entrada."""
    assert main(["-d", "ab"]) == 2
    assert "delimitador" in capsys.readouterr().err


def test_main_same_input_and_output(tmp_path: Path) -> None:
    """Hipótesis: usar el mismo archivo de entrada y salida se rechaza (3)."""
    source = tmp_path / "datos.json"
    source.write_text("[]", encoding="utf-8")
    assert main(["-i", str(source), "-o", str(source)]) == 3
    assert source.read_text(encoding="utf-8") == "[]"


def test_main_output_in_missing_directory(tmp_path: Path) -> None:
    """Hipótesis: una carpeta de salida inexistente devuelve 3."""
    source = tmp_path / "in.json"
    source.write_text("[1]", encoding="utf-8")
    assert main(["-i", str(source), "-o", str(tmp_path / "x" / "out.csv")]) == 3


def test_main_input_not_utf8(tmp_path: Path) -> None:
    """Hipótesis: un archivo que no es UTF-8 válido devuelve 3."""
    source = tmp_path / "in.json"
    source.write_bytes(b"\xff\xfe\x00")
    assert main(["-i", str(source)]) == 3


def test_main_lone_surrogate_cannot_be_encoded(tmp_path: Path) -> None:
    """Hipótesis: un texto no codificable en UTF-8 devuelve 3 sin dejar salida."""
    source = tmp_path / "in.json"
    target = tmp_path / "out.csv"
    source.write_text('["\\ud800"]', encoding="utf-8")
    assert main(["-i", str(source), "-o", str(target)]) == 3
    assert not target.exists()


def test_main_unreadable_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Hipótesis: si la entrada estándar no se puede leer, devuelve 3."""

    class Broken(io.StringIO):
        def read(self, size: int | None = -1) -> str:
            raise OSError("sin entrada")

    monkeypatch.setattr(sys, "stdin", Broken())
    assert main([]) == 3
    assert "entrada estándar" in capsys.readouterr().err


def test_main_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Hipótesis: Ctrl+C termina con 130 y sin traceback."""

    def interrupt(text: str, delimiter: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(module, "convert", interrupt)
    _stdin(monkeypatch, b"[]")
    assert main([]) == 130
    assert "interrumpido" in capsys.readouterr().err


def test_main_unexpected_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Hipótesis: un error imprevisto se informa sin traceback y devuelve 1."""

    def explode(text: str, delimiter: str) -> str:
        raise RuntimeError("falla")

    monkeypatch.setattr(module, "convert", explode)
    _stdin(monkeypatch, b"[]")
    assert main([]) == 1
    assert "error inesperado" in capsys.readouterr().err


def test_main_help_version_and_bad_option(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Hipótesis: -h y -V devuelven 0 y una opción desconocida devuelve 2."""
    assert main(["-h"]) == 0
    assert main(["-V"]) == 0
    assert f"{__version__} (build {__build__})" in capsys.readouterr().out
    assert main(["--no-existe"]) == 2


# --- Ejecución real y metadatos --------------------------------------------


def test_script_runs_as_filter() -> None:
    """Hipótesis: python json2csv.py funciona como filtro de stdin a stdout."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "-d", ";"],
        input=b'[{"a": 1, "b": 2}]',
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.decode().splitlines() == ["a;b", "1;2"]


def test_module_entry_point(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hipótesis: python -m json2csv termina con el código de main."""
    monkeypatch.setattr(sys, "argv", ["json2csv", "-V"])
    with pytest.raises(SystemExit) as info:
        runpy.run_module("json2csv", run_name="__main__")
    assert info.value.code == 0


def test_version_and_build_files_are_in_sync() -> None:
    """Hipótesis: VERSION y BUILD coinciden con el código y con pyproject."""
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == __version__
    assert (ROOT / "BUILD").read_text(encoding="utf-8").strip() == __build__
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "version" in pyproject["project"]["dynamic"]
