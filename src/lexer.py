"""
Analizador léxico (Lex).

Convierte el código fuente en una lista de Token. Las palabras reservadas
(abs, Sin, Cos, Tan, print) se reconocen primero como identificador y luego
se reclasifican consultando KEYWORDS — resolución "implícita", como se vio
en la Clase 3 (Análisis Léxico) del curso.
"""

import re
from dataclasses import dataclass

KEYWORDS = {"abs", "Sin", "Cos", "Tan", "print"}


@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int


class LexicalError(Exception):
    pass


_TOKEN_SPEC = [
    ("NUM", r"\d+(\.\d+)?"),
    ("ID", r"[a-zA-Z_][a-zA-Z_0-9]*"),
    ("ASSIGN", r"="),
    ("SEMI", r";"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("PERCENT", r"%"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

_MASTER_RE = re.compile("|".join(f"(?P<{nombre}>{patron})" for nombre, patron in _TOKEN_SPEC))


def tokenize(source: str):
    tokens = []
    line = 1
    line_start = 0

    for m in _MASTER_RE.finditer(source):
        kind = m.lastgroup
        value = m.group()
        col = m.start() - line_start + 1

        if kind == "NEWLINE":
            line += 1
            line_start = m.end()
            continue
        if kind == "SKIP":
            continue
        if kind == "MISMATCH":
            raise LexicalError(f"Carácter inesperado {value!r} en línea {line}, columna {col}")

        if kind == "ID" and value in KEYWORDS:
            kind = value  # la palabra reservada se vuelve su propio tipo de token

        tokens.append(Token(kind, value, line, col))

    tokens.append(Token("EOF", "", line, 0))
    return tokens
