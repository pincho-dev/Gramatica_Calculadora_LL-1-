from src.lexer import tokenize
from src.ll1_table import CONFLICTOS_LL1, trace_table_driven, PRIMEROS, SIGUIENTES


def test_gramatica_sin_conflictos_ll1():
    # Prueba formal: si no hay conflictos, la gramática es LL(1).
    assert CONFLICTOS_LL1 == []


def test_primeros_factor_incluye_todas_las_formas():
    assert PRIMEROS["Factor"] == {"(", "id", "num", "-", "abs", "Sin", "Cos", "Tan"}


def test_siguientes_expr_prima():
    assert SIGUIENTES["Expr'"] == {";", ")"}


def test_trace_acepta_programa_valido():
    tokens = tokenize("x = 3 + 4 * 2; print(x);")
    assert trace_table_driven(tokens) is True


def test_trace_acepta_funciones_anidadas():
    tokens = tokenize("y = Sin(Cos(0)) + abs(-1);")
    assert trace_table_driven(tokens) is True


def test_trace_rechaza_programa_invalido():
    import pytest
    from src.ll1_table import ErrorTablaLL1

    tokens = tokenize("x = 3 +;")
    with pytest.raises(ErrorTablaLL1):
        trace_table_driven(tokens)
