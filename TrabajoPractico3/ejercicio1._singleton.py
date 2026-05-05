class Factorial:
    _instancia = None #variable de clase

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia
    
    def CalcularFactorial(self, n):
        if n < 0:
            raise ValueError("El número debe ser no negativo")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result


#ejemplo
if __name__ == "__main__":
    try:
        numero = int(input("Ingrese un número para calcular su factorial: "))
        factorial_calculator = Factorial()
        resultado = factorial_calculator.CalcularFactorial(numero)
        print(f"El factorial de {numero} es: {resultado}")
    except ValueError:
        print("Error: Por favor ingrese un número válido.")