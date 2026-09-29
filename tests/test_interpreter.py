import math

import pytest

from src.lexer import tokenize
from src.parser import Parser
from src.interpreter import Interpreter, RuntimeErrorLL1


def run_source(src):
    programa = Parser(tokenize(src)).parse_programa()
    return Interpreter().run(programa)


def test_operaciones_aritmeticas():
    assert run_source("print(3 + 4 * 2);") == [11.0]
    assert run_source("print(10 - 3 - 2);") == [5.0]
    assert run_source("print((1 + 2) * 3);") == [9.0]
    assert run_source("print(7 % 3);") == [1.0]
    assert run_source("print(8 / 4);") == [2.0]


def test_variables_y_reasignacion():
    salida = run_source("x = 10; x = x + 5; print(x);")
    assert salida == [15.0]


def test_funciones_trigonometricas():
    salida = run_source("print(Sin(0)); print(Cos(0)); print(Tan(0));")
    assert salida == pytest.approx([0.0, 1.0, 0.0], abs=1e-9)


def test_abs_y_unario():
    salida = run_source("print(abs(-5)); print(-(-3));")
    assert salida == [5.0, 3.0]


def test_pi_medio_seno_coseno():
    salida = run_source("x = 1.5707963267948966; print(Sin(x)); print(Cos(x));")
    assert salida[0] == pytest.approx(1.0, abs=1e-9)
    assert salida[1] == pytest.approx(0.0, abs=1e-9)


def test_division_por_variable_cero_falla_en_ejecucion():
    with pytest.raises(RuntimeErrorLL1, match="División por cero"):
        run_source("d = 0; print(5 / d);")


def test_programa_completo_ejemplo_basico():
    salida = run_source(
        "x = 3 + 4 * 2;"
        "print(x);"
        "y = Sin(0) + Cos(0);"
        "print(y);"
        "z = abs(-5) - Tan(0);"
        "print(z);"
    )
    assert salida == pytest.approx([11.0, 1.0, 5.0], abs=1e-9)
