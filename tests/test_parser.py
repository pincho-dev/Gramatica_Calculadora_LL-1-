import pytest

from src.lexer import tokenize
from src.parser import Parser, SyntaxErrorLL1
from src.ast_nodes import Assign, Print, BinOp, Num, Var, FuncCall, UnaryMinus


def parse_source(src):
    return Parser(tokenize(src)).parse_programa()


def test_programa_vacio():
    programa = parse_source("")
    assert programa.statements == []


def test_asignacion_simple():
    programa = parse_source("x = 5;")
    assert len(programa.statements) == 1
    stmt = programa.statements[0]
    assert isinstance(stmt, Assign)
    assert stmt.name == "x"
    assert isinstance(stmt.expr, Num)
    assert stmt.expr.value == 5.0


def test_print():
    programa = parse_source("print(1 + 2);")
    stmt = programa.statements[0]
    assert isinstance(stmt, Print)
    assert isinstance(stmt.expr, BinOp)


def test_precedencia_multiplicacion_sobre_suma():
    # 1 + 2 * 3  debe quedar como  1 + (2 * 3)
    programa = parse_source("x = 1 + 2 * 3;")
    expr = programa.statements[0].expr
    assert isinstance(expr, BinOp) and expr.op == "+"
    assert isinstance(expr.left, Num) and expr.left.value == 1.0
    assert isinstance(expr.right, BinOp) and expr.right.op == "*"


def test_asociatividad_izquierda_resta():
    # 10 - 3 - 2 debe quedar como (10 - 3) - 2, NO 10 - (3 - 2)
    programa = parse_source("x = 10 - 3 - 2;")
    expr = programa.statements[0].expr
    assert isinstance(expr, BinOp) and expr.op == "-"
    assert isinstance(expr.left, BinOp) and expr.left.op == "-"
    assert expr.left.left.value == 10.0
    assert expr.left.right.value == 3.0
    assert expr.right.value == 2.0


def test_parentesis_alteran_precedencia():
    programa = parse_source("x = (1 + 2) * 3;")
    expr = programa.statements[0].expr
    assert isinstance(expr, BinOp) and expr.op == "*"
    assert isinstance(expr.left, BinOp) and expr.left.op == "+"


def test_funcion_y_unario():
    programa = parse_source("x = abs(-5) + Sin(0);")
    expr = programa.statements[0].expr
    assert isinstance(expr, BinOp) and expr.op == "+"
    assert isinstance(expr.left, FuncCall) and expr.left.name == "abs"
    assert isinstance(expr.left.arg, UnaryMinus)
    assert isinstance(expr.right, FuncCall) and expr.right.name == "Sin"


def test_varias_sentencias():
    programa = parse_source("x = 1; y = 2; print(x + y);")
    assert len(programa.statements) == 3


@pytest.mark.parametrize("fuente", [
    "x = 3 +;",        # falta operando
    "x = 5",           # falta ';'
    "5 = x;",          # no puede empezar con num
    "x = (1 + 2;",     # falta ')'
    "x = Sin 0);",     # falta '(' tras la función
])
def test_errores_sintacticos(fuente):
    with pytest.raises(SyntaxErrorLL1):
        parse_source(fuente)
