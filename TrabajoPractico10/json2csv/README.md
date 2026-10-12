# json2csv

![CI/CD](https://github.com/JoaquinPoggio/UADER_IS2_POGGIO/actions/workflows/json2csv-ci.yml/badge.svg)

Herramienta de línea de comandos en Python que convierte JSON a CSV con
estrategia de **filtro**: lee de un archivo o de la entrada estándar y escribe
en un archivo o en la salida estándar. No tiene dependencias externas.

Documentación de la API (pdoc): https://joaquinpoggio.github.io/UADER_IS2_POGGIO/

## Instalación

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Uso

```bat
python src\json2csv\json2csv.py [-i ENTRADA] [-o SALIDA] [-d DELIMITADOR]
```

| Opción | Descripción                                                           |
| ------ | --------------------------------------------------------------------- |
| `-i`   | Archivo JSON de entrada. Si se omite, se lee la entrada estándar.     |
| `-o`   | Archivo CSV de salida. Si se omite, se escribe en la salida estándar. |
| `-d`   | Delimitador de un solo carácter (por defecto `,`). `\t` = tabulación. |
| `-V`   | Muestra VERSION y BUILD.                                              |

Ejemplos:

```bat
python src\json2csv\json2csv.py -i datos.json -o salida.csv -d ";"
type datos.json | json2csv -d "\t" > salida.tsv
```

## Reglas de conversión

- Lista de objetos: una fila por objeto. Un objeto suelto: una fila.
- Objetos anidados: columnas `a.b`. Listas: JSON dentro de una celda.
- Elementos que no son objetos: columna `value`. `null` es celda vacía.
- El encabezado es la unión de las claves en orden de aparición.
- Entrada y salida en UTF-8. Las filas terminan en `\n`.

## Códigos de salida

| Código | Significado                                               |
| ------ | --------------------------------------------------------- |
| 0      | Conversión correcta                                       |
| 1      | JSON inválido, estructura no soportada o error inesperado |
| 2      | Argumentos inválidos (por ejemplo, delimitador no válido) |
| 3      | Error de entrada/salida                                   |
| 130    | Interrumpido por el usuario                               |

## Desarrollo

```bat
python -m ruff check .
python -m black --check .
python -m mypy
python -m pyright
python -m bandit -c pyproject.toml -r src
python -m pytest
python -m pdoc --docformat google --output-directory docs json2csv
```

## Versionado

`VERSION` (SemVer) y `BUILD` (entero, +1 por cada PR) deben coincidir con
`__version__` y `__build__` de `src/json2csv/json2csv.py`; un test lo verifica.
Los cambios se registran en `CHANGELOG.md` y los prompts de IA en `CONTEXT.md`.

## Licencia

MIT (ver `LICENSE`).
