#!/usr/bin/python
#*-------------------------------------------------------------------------*
#* factorial.py                                                            *
#* calcula el factorial de un número                                       *
#* Dr.P.E.Colla (c) 2022                                                   *
#* Creative commons                                                        *
#*-------------------------------------------------------------------------*
import sys
def factorial(num): 
    if num < 0: 
        print("Factorial de un número negativo no existe")
        return 0
    elif num == 0: 
        return 1
        
    else: 
        fact = 1
        while(num > 1): 
            fact *= num 
            num -= 1
        return fact 

if len(sys.argv) > 1:
    valor = sys.argv[1]
else:
    valor = input("Ingrese número o rango (ej: 4-8, -10, 5-): ")

# Procesar rangos
if "-" in valor:
    partes = valor.split("-")

    if partes[0] == "":      
        desde = 1
        hasta = int(partes[1])
    elif partes[1] == "":    
        desde = int(partes[0])
        hasta = 60
    else:                   
        desde = int(partes[0])
        hasta = int(partes[1])

    for i in range(desde, hasta + 1):
        print(f"{i}! = {factorial(i)}")
else:
    num = int(valor)
    print("Factorial ", num, "! es ", factorial(num))

