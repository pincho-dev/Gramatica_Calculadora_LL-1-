
EPSILON = "eps"
END = "$"

GRAMMAR = {
    "Programa":   [["ListaSents"]],
    "ListaSents": [["Sent", "ListaSents"], []],
    "Sent":       [["id", "=", "Expr", ";"], ["print", "(", "Expr", ")", ";"]],
    "Expr":       [["Term", "Expr'"]],
    "Expr'":      [["+", "Term", "Expr'"], ["-", "Term", "Expr'"], []],
    "Term":       [["Factor", "Term'"]],
    "Term'":      [["*", "Factor", "Term'"], ["/", "Factor", "Term'"], ["%", "Factor", "Term'"], []],
    "Factor":     [["(", "Expr", ")"], ["id"], ["num"], ["-", "Factor"], ["Funcion", "(", "Expr", ")"], ["angle", "(","Expr", ",", "Expr", ")"]],
    "Funcion":    [["abs"], ["Sin"], ["Cos"], ["Tan"]],
}
NONTERMINALS = set(GRAMMAR)
TERMINALS = {"id", "num", "=", ";", ",", "angle", "print", "(", ")", "+", "-", "*", "/", "%",
            "abs", "Sin", "Cos", "Tan"}
START = "Programa"


def primeros(grammar, nonterminals, terminals):
    tabla = {nt: set() for nt in nonterminals}
    cambio = True
    while cambio:
        cambio = False
        for cabeza, producciones in grammar.items():
            for prod in producciones:
                if prod == []:
                    if EPSILON not in tabla[cabeza]:
                        tabla[cabeza].add(EPSILON)
                        cambio = True
                    continue
                anulable = True
                for simbolo in prod:
                    if simbolo in terminals:
                        if simbolo not in tabla[cabeza]:
                            tabla[cabeza].add(simbolo)
                            cambio = True
                        anulable = False
                        break
                    antes = len(tabla[cabeza])
                    tabla[cabeza] |= (tabla[simbolo] - {EPSILON})
                    if len(tabla[cabeza]) != antes:
                        cambio = True
                    if EPSILON not in tabla[simbolo]:
                        anulable = False
                        break
                if anulable and EPSILON not in tabla[cabeza]:
                    tabla[cabeza].add(EPSILON)
                    cambio = True
    return tabla


def primeros_de_secuencia(seq, primeros_dict, terminals):
    resultado = set()
    anulable = True
    for simbolo in seq:
        if simbolo in terminals:
            resultado.add(simbolo)
            anulable = False
            break
        resultado |= (primeros_dict[simbolo] - {EPSILON})
        if EPSILON not in primeros_dict[simbolo]:
            anulable = False
            break
    if anulable:
        resultado.add(EPSILON)
    return resultado


def siguientes(grammar, nonterminals, terminals, start, primeros_dict):
    tabla = {nt: set() for nt in nonterminals}
    tabla[start].add(END)
    cambio = True
    while cambio:
        cambio = False
        for cabeza, producciones in grammar.items():
            for prod in producciones:
                for i, simbolo in enumerate(prod):
                    if simbolo not in nonterminals:
                        continue
                    resto = prod[i + 1:]
                    primeros_resto = (
                        primeros_de_secuencia(resto, primeros_dict, terminals)
                        if resto else {EPSILON}
                    )
                    antes = len(tabla[simbolo])
                    tabla[simbolo] |= (primeros_resto - {EPSILON})
                    if EPSILON in primeros_resto:
                        tabla[simbolo] |= tabla[cabeza]
                    if len(tabla[simbolo]) != antes:
                        cambio = True
    return tabla


def prediccion(grammar, primeros_dict, siguientes_dict, terminals):
    tabla = {}
    for cabeza, producciones in grammar.items():
        for idx, prod in enumerate(producciones):
            primeros_prod = (
                {EPSILON} if prod == []
                else primeros_de_secuencia(prod, primeros_dict, terminals)
            )
            resultado = primeros_prod - {EPSILON}
            if EPSILON in primeros_prod:
                resultado |= siguientes_dict[cabeza]
            tabla[(cabeza, idx)] = resultado
    return tabla


def build_table(grammar, primeros_dict, siguientes_dict, terminals):
    tabla = {}
    conflictos = []
    for cabeza, producciones in grammar.items():
        for prod in producciones:
            primeros_prod = (
                {EPSILON} if prod == []
                else primeros_de_secuencia(prod, primeros_dict, terminals)
            )
            celdas = set(primeros_prod - {EPSILON})
            if EPSILON in primeros_prod:
                celdas |= siguientes_dict[cabeza]
            for a in celdas:
                clave = (cabeza, a)
                if clave in tabla and tabla[clave] != prod:
                    conflictos.append((clave, tabla[clave], prod))
                tabla[clave] = prod
    return tabla, conflictos


PRIMEROS = primeros(GRAMMAR, NONTERMINALS, TERMINALS)
SIGUIENTES = siguientes(GRAMMAR, NONTERMINALS, TERMINALS, START, PRIMEROS)
PREDICCION = prediccion(GRAMMAR, PRIMEROS, SIGUIENTES, TERMINALS)
TABLA_LL1, CONFLICTOS_LL1 = build_table(GRAMMAR, PRIMEROS, SIGUIENTES, TERMINALS)


TOKEN_TO_TERMINAL = {
    "ID": "id", "NUM": "num", "ASSIGN": "=", "SEMI": ";",
    "LPAREN": "(", "RPAREN": ")", "PLUS": "+", "MINUS": "-",
    "STAR": "*", "SLASH": "/", "PERCENT": "%",
    "abs": "abs", "Sin": "Sin", "Cos": "Cos", "Tan": "Tan", "print": "print",
    "COMA": ",", "angle": "angle", 
    "EOF": END,
}


class ErrorTablaLL1(Exception):
    pass


def trace_table_driven(tokens, verbose=False):
    entrada = [TOKEN_TO_TERMINAL[t.type] for t in tokens]
    pila = [END, START]
    i = 0
    while pila:
        tope = pila[-1]
        actual = entrada[i]
        if tope == actual:
            if verbose:
                print(f"{pila} | {entrada[i:]} | coincidir {actual}")
            pila.pop()
            i += 1
        elif tope in NONTERMINALS:
            prod = TABLA_LL1.get((tope, actual))
            if prod is None:
                raise ErrorTablaLL1(f"No hay regla para [{tope}, {actual}]")
            if verbose:
                cuerpo = " ".join(prod) if prod else "ε"
                print(f"{pila} | {entrada[i:]} | {tope} → {cuerpo}")
            pila.pop()
            for simbolo in reversed(prod):
                pila.append(simbolo)
        else:
            raise ErrorTablaLL1(f"Se esperaba '{tope}' y se encontró '{actual}'")
    return True


if __name__ == "__main__":
    print("PRIMEROS:")
    for nt in sorted(NONTERMINALS):
        print(f"  {nt}: {sorted(PRIMEROS[nt])}")
    print("\nSIGUIENTES:")
    for nt in sorted(NONTERMINALS):
        print(f"  {nt}: {sorted(SIGUIENTES[nt])}")
    print("\nPREDICCIÓN:")
    for (cabeza, idx), conjunto in PREDICCION.items():
        prod = GRAMMAR[cabeza][idx]
        prod_str = " ".join(prod) if prod else "eps"
        print(f"  {cabeza} -> {prod_str}: {sorted(conjunto)}")
    print(f"\n¿Conflictos LL(1)? {'Sí -> ' + str(CONFLICTOS_LL1) if CONFLICTOS_LL1 else 'No — la gramática es LL(1).'}")
