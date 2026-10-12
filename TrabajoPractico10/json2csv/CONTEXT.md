# CONTEXT.md - Uso de herramientas de IA

Herramienta: Claude (Anthropic). Fecha: 2026-10-09.

## Prompt 1

• Desarrolle una herramienta en lenguaje Python para convertir archivos de formato JSON a formato CSV. El programa deberá implementarse con una estrategia de filtro. El formato de ejecución será: python json2csv.py {-i input.txt} {-o output.txt} {-d delimitador} Si no se informa el argumento “-i“ el programa podrá aceptar el archivo de entrada mediante entrada estándar, al mismo tiempo si no se informa el argumento “-o” se emitirá el texto resultante mediante salida estándar. Se utilizará la coma como delimitador, excepto que se indique uno distinto con el argumento “-d”
• Asegure la implementación de controles robustos para las condiciones de excepción que pueda encontrar durante la ejecución. Implemente el proyecto en GitHub utilizando un marco para integración continua con las siguientes características:
a. Todo el desarrollo lo realizará utilizando un ambiente virtual Python (venv).
b. Esqueleto de proyecto basado en CookieCutter
c. En el caso de utilizar herramientas de IA documentará los prompts utilizados en el archivo CONTEXT.md
d. La naturaleza del proyecto se mantendrá actualizada en un archivo README.md
e. Los cambios se registrarán en un archivo llamado CHANGELOG.md
f. Genere un archivo REQUIREMENTS.TXT para listar todas las librerías que pueda necesitar el proyecto para funcionar de forma de generarlas como parte de un ambiente virtual Python.
g. La licencia del proyecto será MIT y se generará documentación automáticamente con pdoc o sphynx
h. Se llevará registro de VERSION y BUILD
i. Ejecutar ruff para validar las reglas de formato y que no de errores.
j. Ejecutar black para validar el formato consistente.
k. Utilizar y validar el correcto uso de reglas de formateo PEP8.
l. Utilizar el correcto uso de convenciones PEP257 para los docstrings, aceptar solo si no hay errores.
m. Ejecutar MyPy para los modulos dentro de alcance, aceptar solo si no hay errores.
n. Ejecutar PyRight para los modulos dentro de alcance, aceptar solo si no hay errores.
o. Test unitario con Pytest con hipótesis de test unitario que permitan la cobertura del 85% o mejor.
p. Utilizar bandit para la evaluación básica de seguridad y que no queden observaciones.
q. No utilizar Trufflehog en los controles de seguridad.
r. Producir una documentación básica del funcionamiento del módulos y actualizarla con cada PR exitoso.
s. Actualizar archivo requirements.txt que se usará para las dependencias de librerías.
t. Se automatizará un workflow en github integrando la fase de CI/CD completa.
u. Con cada PR exitoso genera o actualiza la focumentación básica con pdoc o sphinx. Opcionalmente puede utilizar herramientas de IA para desplegar el proyecto.

Resultado: estructura del proyecto, módulo, tests, workflow de CI/CD y documentos.

## Prompt 2

vamos paso a paso, desde 0
