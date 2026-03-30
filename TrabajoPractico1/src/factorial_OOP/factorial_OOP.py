import sys

class Factorial:
    def __init__(self):
        """Constructor, no recibe parámetros"""
        pass

    def run(self, min_val, max_val):
        """Calcula factoriales desde min_val hasta max_val"""
        for n in range(min_val, max_val + 1):
            print(f"{n}! = {self._factorial(n)}")

    def _factorial(self, num):
        """Método privado para calcular factorial de un número"""
        if num < 0:
            print(f"Factorial de un número negativo ({num}) no existe")
            return 0
        elif num == 0:
            return 1
        else:
            fact = 1
            while num > 1:
                fact *= num
                num -= 1
            return fact

def parse_input(arg):
    """Procesa la entrada tipo número o rango"""
    if "-" in arg:
        partes = arg.split("-")
        if partes[0] == "":
            return 1, int(partes[1])
        elif partes[1] == "":
            return int(partes[0]), 60 
        else:
            return int(partes[0]), int(partes[1]) 
    else:
        val = int(arg)
        return val, val

if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = input("Ingrese un número o rango (ej: 4-8, -10, 5-): ")

min_val, max_val = parse_input(arg)

# Crear objeto Factorial y ejecutar
f = Factorial()
f.run(min_val, max_val)
