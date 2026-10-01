
from dataclasses import dataclass
from typing import List, Union


@dataclass
class Num:
    value: float
    line: int


@dataclass
class Var:
    name: str
    line: int


@dataclass
class UnaryMinus:
    expr: "Expr"
    line: int


@dataclass
class BinOp:
    op: str
    left: "Expr"
    right: "Expr"
    line: int


@dataclass
class FuncCall:
    name: str
    arg: "Expr"
    line: int




@dataclass
class Assign:
    name: str
    expr: Expr
    line: int


@dataclass
class Print:
    expr: Expr
    line: int


Stmt = Union[Assign, Print]


@dataclass
class Program:
    statements: List[Stmt]

@dataclass
class Angle:
    expr1: Expr
    expr2: Expr
    line: int
    
Expr = Union[Num, Var, UnaryMinus, BinOp, FuncCall, Angle]
