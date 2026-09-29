"""Punto de entrada: Lex -> Sintáctico -> Semántico -> Intérprete."""

import sys

from .lexer import tokenize, LexicalError
from .parser import Parser, SyntaxErrorLL1
from .semantic import SemanticAnalyzer, SemanticError
from .interpreter import Interpreter, RuntimeErrorLL1


def run(source: str):
    tokens = tokenize(source)
    programa = Parser(tokens).parse_programa()
    SemanticAnalyzer().analyze(programa)
    return Interpreter().run(programa)


def main():
    if len(sys.argv) != 2:
        print("Uso: python -m src.main archivo.txt")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        source = f.read()

    try:
        run(source)
    except (LexicalError, SyntaxErrorLL1, SemanticError, RuntimeErrorLL1) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
