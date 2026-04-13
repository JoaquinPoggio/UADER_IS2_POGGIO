import unittest
from rpn import RPN, RPNError
import math

class TestRPN(unittest.TestCase):

    def setUp(self):
        self.rpn = RPN()

    # --- Operaciones básicas ---
    def test_suma(self):
        self.assertEqual(self.rpn.eval("3 4 +".split()), 7)

    def test_expresion_compleja(self):
        self.assertEqual(self.rpn.eval("5 1 2 + 4 * + 3 -".split()), 14)

    def test_multiplicacion_y_suma(self):
        self.assertEqual(self.rpn.eval("2 3 4 * +".split()), 14)

    def test_division(self):
        self.assertEqual(self.rpn.eval("8 2 /".split()), 4)

    # --- Floats ---
    def test_float(self):
        self.assertAlmostEqual(self.rpn.eval("2.5 2 *".split()), 5.0)

    def test_negativos(self):
        self.assertEqual(self.rpn.eval("-3 -2 *".split()), 6)

    # --- Errores ---
    def test_division_por_cero(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("3 0 /".split())

    def test_token_invalido(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("3 x +".split())

    def test_pila_insuficiente(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("+".split())

    def test_pila_final_incorrecta(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("3 4".split())

    # --- Stack ops ---
    def test_dup(self):
        self.assertEqual(self.rpn.eval("5 dup *".split()), 25)

    def test_swap(self):
        self.assertEqual(self.rpn.eval("3 4 swap -".split()), 1)

    def test_drop(self):
        self.assertEqual(self.rpn.eval("3 4 drop".split()), 3)

    def test_swap_error(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("1 swap".split())

    def test_dup_error(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("dup".split())

    def test_drop_error(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("drop".split())

    def test_clear(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("3 4 clear".split())

    # --- Funciones ---
    def test_sqrt(self):
        self.assertEqual(self.rpn.eval("9 sqrt".split()), 3)

    def test_log(self):
        self.assertEqual(self.rpn.eval("100 log".split()), 2)

    def test_ln(self):
        self.assertAlmostEqual(self.rpn.eval("1 ln".split()), 0)

    def test_ex(self):
        self.assertAlmostEqual(self.rpn.eval("1 ex".split()), math.e)

    def test_10x(self):
        self.assertEqual(self.rpn.eval("2 10x".split()), 100)

    def test_yx(self):
        self.assertEqual(self.rpn.eval("2 3 yx".split()), 8)

    def test_yx_error(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("2 yx".split())

    def test_inverso(self):
        self.assertEqual(self.rpn.eval("2 1/x".split()), 0.5)

    def test_inverso_cero(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("0 1/x".split())

    def test_chs(self):
        self.assertEqual(self.rpn.eval("5 chs".split()), -5)

    # --- Trigonometría ---
    def test_sin(self):
        self.assertAlmostEqual(self.rpn.eval("90 sin".split()), 1, places=5)

    def test_cos(self):
        self.assertAlmostEqual(self.rpn.eval("0 cos".split()), 1, places=5)

    def test_tg(self):
        self.assertAlmostEqual(self.rpn.eval("45 tg".split()), 1, places=5)

    def test_asin(self):
        self.assertAlmostEqual(self.rpn.eval("1 asin".split()), 90, places=5)

    def test_acos(self):
        self.assertAlmostEqual(self.rpn.eval("1 acos".split()), 0, places=5)

    def test_atg(self):
        self.assertAlmostEqual(self.rpn.eval("1 atg".split()), 45, places=5)

    # --- Memoria ---
    def test_memoria(self):
        self.assertEqual(self.rpn.eval("5 0 sto 0 rcl".split()), 5)

    def test_memoria_invalida_sto(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("5 99 sto".split())

    def test_memoria_invalida_rcl(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("99 rcl".split())

    def test_sto_pila_insuficiente(self):
        with self.assertRaises(RPNError):
            self.rpn.eval("5 sto".split())

    # --- Constantes ---
    def test_pi(self):
        self.assertAlmostEqual(self.rpn.eval("p".split()), math.pi)

    def test_phi(self):
        self.assertAlmostEqual(self.rpn.eval("j".split()), (1+math.sqrt(5))/2)


if __name__ == "__main__":
    unittest.main()