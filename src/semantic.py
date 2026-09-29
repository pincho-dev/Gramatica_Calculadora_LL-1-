"""
Análisis semántico.

Recorre el AST ya construido por el parser y verifica dos reglas que la
sintaxis por sí sola no puede garantizar:

1. Toda variable debe haber sido asignada antes de usarse en una expresión
   (se mantiene una tabla de símbolos que crece con cada asignación).
2. División o módulo por una constante literal 0 se rechaza en tiempo de
   análisis (si el divisor es una variable, el chequeo se hace en tiempo de
   ejecución — ver interpreter.py).
"""

from .ast_nodes import Assign, Print, Num, Var, UnaryMinus, BinOp, FuncCall


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = set()

    def analyze(self, program):
        for stmt in program.statements:
            self._check_stmt(stmt)

    def _check_stmt(self, stmt):
        if isinstance(stmt, Assign):
            self._check_expr(stmt.expr)
            self.symbols.add(stmt.name)
        elif isinstance(stmt, Print):
            self._check_expr(stmt.expr)
        else:
            raise SemanticError(f"Sentencia desconocida: {stmt}")

    def _check_expr(self, expr):
        if isinstance(expr, Num):
            return
        if isinstance(expr, Var):
            if expr.name not in self.symbols:
                raise SemanticError(
                    f"Variable '{expr.name}' usada sin haber sido asignada (línea {expr.line})"
                )
            return
        if isinstance(expr, UnaryMinus):
            self._check_expr(expr.expr)
            return
        if isinstance(expr, FuncCall):
            self._check_expr(expr.arg)
            return
        if isinstance(expr, BinOp):
            self._check_expr(expr.left)
            self._check_expr(expr.right)
            if expr.op in ("/", "%") and isinstance(expr.right, Num) and expr.right.value == 0:
                raise SemanticError(
                    f"División por cero detectada en línea {expr.line} (operador '{expr.op}' entre 0)"
                )
            return
        raise SemanticError(f"Expresión desconocida: {expr}")
