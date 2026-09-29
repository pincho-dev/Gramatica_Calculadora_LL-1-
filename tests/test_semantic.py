import pytest

from src.lexer import tokenize
from src.parser import Parser
from src.semantic import SemanticAnalyzer, SemanticError


def analyze_source(src):
    programa = Parser(tokenize(src)).parse_programa()
    SemanticAnalyzer().analyze(programa)


def test_programa_valido_no_lanza_error():
    analyze_source("x = 1; y = x + 2; print(y);")


def test_variable_no_asignada():
    with pytest.raises(SemanticError, match="sin haber sido asignada"):
        analyze_source("print(w);")


def test_variable_asignada_despues_de_su_uso_falla():
    with pytest.raises(SemanticError):
        analyze_source("print(w); w = 1;")


def test_division_por_cero_literal():
    with pytest.raises(SemanticError, match="División por cero"):
        analyze_source("x = 5 / 0;")


def test_modulo_por_cero_literal():
    with pytest.raises(SemanticError, match="División por cero"):
        analyze_source("x = 5 % 0;")


def test_division_por_variable_no_falla_en_semantico():
    # el valor de la variable solo se conoce en ejecución, no es error semántico
    analyze_source("d = 0; x = 5 / d;")
