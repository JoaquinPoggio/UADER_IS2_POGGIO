#!/usr/bin/env python3
"""Calculadora RPN con soporte de operaciones, funciones y memoria."""

import sys
import math


class RPNError(Exception):
    """Excepción personalizada para errores de la calculadora RPN."""

    pass


class RPN:
    """Implementación de una calculadora RPN basada en pila."""

    def __init__(self):
        self.stack = []
        self.mem = {f"{i:02d}": 0.0 for i in range(10)}
        self.consts = {"p": math.pi, "e": math.e, "j": (1 + math.sqrt(5)) / 2}

    def push(self, x):
        """Agrega un número a la pila."""
        self.stack.append(float(x))

    def pop(self):
        """Extrae el último elemento de la pila."""
        if not self.stack:
            raise RPNError("Pila insuficiente")
        return self.stack.pop()

    def eval(self, tokens):
        """Evalúa una expresión en notación polaca inversa."""
        for t in tokens:
            if t in self.consts:
                self.push(self.consts[t])

            elif t in {"+", "-", "*", "/"}:
                if len(self.stack) < 2:
                    raise RPNError("Pila insuficiente para operar")
                b = self.pop()
                a = self.pop()

                if t == "+":
                    self.push(a + b)
                elif t == "-":
                    self.push(a - b)
                elif t == "*":
                    self.push(a * b)
                elif t == "/":
                    if b == 0:
                        raise RPNError("División por cero")
                    self.push(a / b)

            elif t == "dup":
                if not self.stack:
                    raise RPNError("Pila insuficiente")
                self.push(self.stack[-1])

            elif t == "swap":
                if len(self.stack) < 2:
                    raise RPNError("Pila insuficiente")
                self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

            elif t == "drop":
                self.pop()

            elif t == "clear":
                self.stack.clear()

            elif t == "sqrt":
                self.push(math.sqrt(self.pop()))

            elif t == "log":
                self.push(math.log10(self.pop()))

            elif t == "ln":
                self.push(math.log(self.pop()))

            elif t == "ex":
                self.push(math.exp(self.pop()))

            elif t == "10x":
                self.push(10 ** self.pop())

            elif t == "yx":
                if len(self.stack) < 2:
                    raise RPNError("Pila insuficiente")
                b = self.pop()
                a = self.pop()
                self.push(a**b)

            elif t == "1/x":
                x = self.pop()
                if x == 0:
                    raise RPNError("División por cero")
                self.push(1 / x)

            elif t == "chs":
                self.push(-self.pop())

            elif t in {"sin", "cos", "tg", "asin", "acos", "atg"}:
                x = self.pop()

                if t in {"sin", "cos", "tg"}:
                    x = math.radians(x)

                if t == "sin":
                    self.push(math.sin(x))
                elif t == "cos":
                    self.push(math.cos(x))
                elif t == "tg":
                    self.push(math.tan(x))
                elif t == "asin":
                    self.push(math.degrees(math.asin(x)))
                elif t == "acos":
                    self.push(math.degrees(math.acos(x)))
                elif t == "atg":
                    self.push(math.degrees(math.atan(x)))

            elif t == "sto":
                if len(self.stack) < 2:
                    raise RPNError("Pila insuficiente")
                addr = str(int(self.pop())).zfill(2)
                if addr not in self.mem:
                    raise RPNError("Memoria inválida")
                self.mem[addr] = self.pop()

            elif t == "rcl":
                addr = str(int(self.pop())).zfill(2)
                if addr not in self.mem:
                    raise RPNError("Memoria inválida")
                self.push(self.mem[addr])

            else:
                try:
                    self.push(float(t))
                except Exception as exc:
                    raise RPNError(f"Token inválido: {t}") from exc

        if len(self.stack) != 1:
            raise RPNError("La pila no terminó con exactamente un valor")

        return self.pop()


def main():
    """Función principal para ejecutar la calculadora desde consola."""
    try:
        expr = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("RPN> ")
        tokens = expr.strip().split()
        rpn = RPN()
        result = rpn.eval(tokens)
        print(result)
    except RPNError as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
