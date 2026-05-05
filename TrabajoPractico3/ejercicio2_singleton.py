class Calculadora:
    _instancia = None
   
    IVA = 0.21
    IIBB = 0.05
    CONTRIBUCIONES = 0.012

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(Calculadora, cls).__new__(cls)
        return cls._instancia
    
    def calcular_total(self, base_inponible):
        iva = base_inponible * self.IVA
        iibb = base_inponible * self.IIBB
        constribuciones = base_inponible * self.CONTRIBUCIONES

        return iva + iibb + constribuciones

calc1 = Calculadora()


base = float(input("Ingrese la base imponible: "))  # True, ambas variables apuntan a la misma instancia

resultado = calc1.calcular_total(base)
print(f"El total a pagar es: {resultado}")
