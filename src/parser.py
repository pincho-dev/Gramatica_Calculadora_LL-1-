"""
Gramática implementada:

    Programa    -> ListaSents
    ListaSents  -> Sent ListaSents | eps
    Sent        -> id = Expr ;
                 | print ( Expr ) ;
    Expr        -> Term Expr'
    Expr'       -> + Term Expr' | - Term Expr' | eps
    Term        -> Factor Term'
    Term'       -> * Factor Term' | / Factor Term' | % Factor Term' | eps
    Factor      -> ( Expr ) | id | num | - Factor | Funcion ( Expr )
    Funcion     -> abs | Sin | Cos | Tan
"""

from .ast_nodes import Program, Assign, Print, Num, Var, UnaryMinus, BinOp, FuncCall, Angle


class SyntaxErrorLL1(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, tipo):
        if self.current.type != tipo:
            raise SyntaxErrorLL1(
                f"Se esperaba '{tipo}' pero se encontró '{self.current.value or self.current.type}' "
                f"en línea {self.current.line}, columna {self.current.col}"
            )
        return self.advance()

    # Programa -> ListaSents
    def parse_programa(self) -> Program:
        stmts = self.parse_lista_sents()
        self.expect("EOF")
        return Program(stmts)

    # ListaSents -> Sent ListaSents | eps      PRED: {id,print} / {$}
    def parse_lista_sents(self):
        if self.current.type in ("ID", "print"):
            sent = self.parse_sent()
            resto = self.parse_lista_sents()
            return [sent] + resto
        if self.current.type == "EOF":
            return []
        raise SyntaxErrorLL1(
            f"Se esperaba una sentencia (identificador o 'print') o fin de archivo, "
            f"pero se encontró '{self.current.value or self.current.type}' en línea {self.current.line}"
        )

    # Sent -> id = Expr ; | print ( Expr ) ;   PRED: {id} / {print}
    def parse_sent(self):
        if self.current.type == "ID":
            tok = self.advance()
            self.expect("ASSIGN")
            expr = self.parse_expr()
            self.expect("SEMI")
            return Assign(tok.value, expr, tok.line)
        if self.current.type == "print":
            tok = self.advance()
            self.expect("LPAREN")
            expr = self.parse_expr()
            self.expect("RPAREN")
            self.expect("SEMI")
            return Print(expr, tok.line)
        raise SyntaxErrorLL1(f"Sentencia inválida en línea {self.current.line}")

    # Expr -> Term Expr'
    def parse_expr(self):
        left = self.parse_term()
        return self.parse_expr_prime(left)

    # Expr' -> + Term Expr' | - Term Expr' | eps   PRED: {+} / {-} / {; )}
    def parse_expr_prime(self, left):
        if self.current.type == "PLUS":
            tok = self.advance()
            right = self.parse_term()
            return self.parse_expr_prime(BinOp("+", left, right, tok.line))
        if self.current.type == "MINUS":
            tok = self.advance()
            right = self.parse_term()
            return self.parse_expr_prime(BinOp("-", left, right, tok.line))
        if self.current.type in ("SEMI", "RPAREN", "COMA"):
            return left
        raise SyntaxErrorLL1(
            f"Operador o fin de expresión inválido: '{self.current.value or self.current.type}' "
            f"en línea {self.current.line}"
        )

    # Term -> Factor Term'
    def parse_term(self):
        left = self.parse_factor()
        return self.parse_term_prime(left)

    # Term' -> * Factor Term' | / Factor Term' | % Factor Term' | eps
    def parse_term_prime(self, left):
        if self.current.type in ("STAR", "SLASH", "PERCENT"):
            op_tok = self.advance()
            op = {"STAR": "*", "SLASH": "/", "PERCENT": "%"}[op_tok.type]
            right = self.parse_factor()
            return self.parse_term_prime(BinOp(op, left, right, op_tok.line))
        if self.current.type in ("PLUS", "MINUS", "SEMI", "RPAREN", "COMA"):
            return left
        raise SyntaxErrorLL1(
            f"Operador o fin de expresión inválido: '{self.current.value or self.current.type}' "
            f"en línea {self.current.line}"
        )

    # Factor -> ( Expr ) | id | num | - Factor | Funcion ( Expr )
    def parse_factor(self):
        tok = self.current
        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN")
            return expr
        if tok.type == "ID":
            self.advance()
            return Var(tok.value, tok.line)
        if tok.type == "NUM":
            self.advance()
            return Num(float(tok.value), tok.line)
        if tok.type == "MINUS":
            self.advance()
            return UnaryMinus(self.parse_factor(), tok.line)
        if tok.type in ("abs", "Sin", "Cos", "Tan"):
            self.advance()
            self.expect("LPAREN")
            expr = self.parse_expr()
            self.expect("RPAREN")
            return FuncCall(tok.type, expr, tok.line)
        if tok.type == "ANGLE":
            self.advance()
            self.expect("LPAREN")
            expr1 = self.parse_expr()
            self.expect("COMA")
            expr2 = self.parse_expr()
            self.expect("RPAREN")
            return Angle(expr1, expr2, tok.line)
        
        raise SyntaxErrorLL1(
            f"Se esperaba un valor, variable, '(' o función, pero se encontró "
            f"'{tok.value or tok.type}' en línea {tok.line}, columna {tok.col}"
        )


def parse(tokens) -> Program:
    return Parser(tokens).parse_programa()
