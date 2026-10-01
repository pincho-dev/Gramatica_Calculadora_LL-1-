"""
Intérprete: recorre el AST y ejecuta el programa (evalúa expresiones,
guarda variables, imprime resultados de `print(...)`).
"""

import math

from .ast_nodes import Assign, Print, Num, Var, UnaryMinus, BinOp, FuncCall, Angle


class RuntimeErrorLL1(Exception):
    pass


FUNCS = {
    "abs": abs,
    "Sin": math.sin,
    "Cos": math.cos,
    "Tan": math.tan,
}


class Interpreter:
    def __init__(self):
        self.vars = {}
        self.output = []

    def run(self, program):
        for stmt in program.statements:
            self._exec(stmt)
        return self.output

    def _exec(self, stmt):
        if isinstance(stmt, Assign):
            self.vars[stmt.name] = self._eval(stmt.expr)
        elif isinstance(stmt, Print):
            value = self._eval(stmt.expr)
            self.output.append(value)
            print(value)
        else:
            raise RuntimeErrorLL1(f"Sentencia desconocida: {stmt}")

    def _eval(self, expr):
        if isinstance(expr, Num):
            return expr.value
        if isinstance(expr, Var):
            if expr.name not in self.vars:
                raise RuntimeErrorLL1(f"Variable '{expr.name}' no definida (línea {expr.line})")
            return self.vars[expr.name]
        if isinstance(expr, UnaryMinus):
            return -self._eval(expr.expr)
        if isinstance(expr, FuncCall):
            return FUNCS[expr.name](self._eval(expr.arg))
        if isinstance(expr, Angle):
            return math.atan2(self._eval(expr.expr1), self._eval(expr.expr2))
        if isinstance(expr, BinOp):
            left = self._eval(expr.left)
            right = self._eval(expr.right)
            if expr.op == "+":
                return left + right
            if expr.op == "-":
                return left - right
            if expr.op == "*":
                return left * right
            if expr.op == "/":
                if right == 0:
                    raise RuntimeErrorLL1(f"División por cero en línea {expr.line}")
                return left / right
            if expr.op == "%":
                if right == 0:
                    raise RuntimeErrorLL1(f"Módulo por cero en línea {expr.line}")
                return left % right
            raise RuntimeErrorLL1(f"Operador desconocido: {expr.op}")
        raise RuntimeErrorLL1(f"Nodo AST desconocido: {expr}")
