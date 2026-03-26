
import matplotlib.pyplot as plt

# Función para calcular iteraciones de Collatz
def collatz_iterations(n):
    count = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        count += 1
    return count

# Listas para graficar
x_iters = []
y_numbers = []

# Calcular Collatz para números 1 a 10000
for n in range(1, 10001):
    x_iters.append(collatz_iterations(n))
    y_numbers.append(n)

# Crear gráfico
plt.figure(figsize=(10,6))
plt.scatter(x_iters, y_numbers, s=1, color='blue')
plt.title("Número de Collatz: iteraciones vs número inicial")
plt.xlabel("Cantidad de iteraciones hasta 1")
plt.ylabel("Número inicial (n)")
plt.grid(True)
plt.show()