import pytest

from src.lexer import tokenize, LexicalError


def test_tokens_basicos():
    tokens = tokenize("x = 3.5 + abs(-2);")
    tipos = [t.type for t in tokens]
    assert tipos == [
        "ID", "ASSIGN", "NUM", "PLUS", "abs", "LPAREN", "MINUS", "NUM",
        "RPAREN", "SEMI", "EOF",
    ]


def test_palabras_reservadas():
    tokens = tokenize("Sin Cos Tan print abs")
    tipos = [t.type for t in tokens]
    assert tipos == ["Sin", "Cos", "Tan", "print", "abs", "EOF"]


def test_identificador_no_confunde_con_reservada():
    # 'absoluto' no es la palabra reservada 'abs', debe seguir siendo ID
    tokens = tokenize("absoluto = 1;")
    assert tokens[0].type == "ID"
    assert tokens[0].value == "absoluto"


def test_numeros_enteros_y_reales():
    tokens = tokenize("10 3.1416")
    assert [t.value for t in tokens if t.type == "NUM"] == ["10", "3.1416"]


def test_lineas_y_columnas():
    tokens = tokenize("x = 1;\ny = 2;")
    y_tok = next(t for t in tokens if t.type == "ID" and t.value == "y")
    assert y_tok.line == 2


def test_caracter_invalido_lanza_error():
    with pytest.raises(LexicalError):
        tokenize("x = @;")
