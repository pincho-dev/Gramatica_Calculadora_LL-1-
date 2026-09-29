# Lenguajes LL(1) — calculadora con funciones y variables

**Asignatura:** Lenguajes de Programación y Transducción · Universidad Sergio Arboleda

Intérprete de un lenguaje de expresiones aritméticas construido **a mano**
(sin ANTLR ni generadores): lexer, parser LL(1) recursivo-descendente,
análisis semántico e intérprete, todo implementado directamente sobre la
teoría de PRIMEROS/SIGUIENTES/PREDICCIÓN vista en clase.

## Integrantes

- Juan Pablo Orjuela
- Santiago Ortengon 
- Julian Beltran Rodriguez 

```
x = 3 + 4 * 2;
print(x);
y = Sin(0) + Cos(0);
print(y);
z = abs(-5) - Tan(0);
print(z);
```

##  El lenguaje

- Operadores aritméticos: `+ - * / %`
- Funciones: `abs`, `Sin`, `Cos`, `Tan` (trigonométricas en **radianes**)
- Asignación de variables: `id = expr;`
- Impresión de resultados: `print(expr);` (necesario para poder observar y
  probar el intérprete)
- Paréntesis para alterar precedencia, menos unario, y funciones anidadas
  (`Sin(Cos(0))`)

##  Gramática LL(1)

```
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
```

**Por qué ya es LL(1) sin necesitar transformaciones:**
- **Sin recursión izquierda:** la suma/resta y la multiplicación/división/
  módulo están escritas con recursión por la derecha (`Expr'`, `Term'`),
  el patrón estándar `E -> E+T|T` ⟹ `E -> TE'`, `E' -> +TE'|eps`.
- **Sin prefijos comunes:** cada alternativa de `Factor` arranca con un
  terminal distinto (`(`, `id`, `num`, `-`, o una palabra de `Funcion`).

##  Conjuntos PRIMEROS

| No terminal | PRIMEROS |
|---|---|
| Funcion | {abs, Sin, Cos, Tan} |
| Factor | {`(`, id, num, `-`, abs, Sin, Cos, Tan} |
| Term' | {`*`, `/`, `%`, eps} |
| Term | {`(`, id, num, `-`, abs, Sin, Cos, Tan} |
| Expr' | {`+`, `-`, eps} |
| Expr | {`(`, id, num, `-`, abs, Sin, Cos, Tan} |
| Sent | {id, print} |
| ListaSents | {id, print, eps} |
| Programa | {id, print, eps} |

##  Conjuntos SIGUIENTES

| No terminal | SIGUIENTES |
|---|---|
| Programa | {$} |
| ListaSents | {$} |
| Sent | {id, print, $} |
| Expr | {`;`, `)`} |
| Expr' | {`;`, `)`} |
| Term | {`+`, `-`, `;`, `)`} |
| Term' | {`+`, `-`, `;`, `)`} |
| Factor | {`*`, `/`, `%`, `+`, `-`, `;`, `)`} |
| Funcion | {`(`} |

##  PREDICCIÓN por producción

| Producción | PRED |
|---|---|
| Programa -> ListaSents | {id, print, $} |
| ListaSents -> Sent ListaSents | {id, print} |
| ListaSents -> eps | {$} |
| Sent -> id = Expr ; | {id} |
| Sent -> print ( Expr ) ; | {print} |
| Expr -> Term Expr' | {`(`, id, num, `-`, abs, Sin, Cos, Tan} |
| Expr' -> + Term Expr' | {`+`} |
| Expr' -> - Term Expr' | {`-`} |
| Expr' -> eps | {`;`, `)`} |
| Term -> Factor Term' | {`(`, id, num, `-`, abs, Sin, Cos, Tan} |
| Term' -> * Factor Term' | {`*`} |
| Term' -> / Factor Term' | {`/`} |
| Term' -> % Factor Term' | {`%`} |
| Term' -> eps | {`+`, `-`, `;`, `)`} |
| Factor -> ( Expr ) | {`(`} |
| Factor -> id | {id} |
| Factor -> num | {num} |
| Factor -> - Factor | {`-`} |
| Factor -> Funcion ( Expr ) | {abs, Sin, Cos, Tan} |
| Funcion -> abs / Sin / Cos / Tan | {abs} / {Sin} / {Cos} / {Tan} |

Estos tres conjuntos y la tabla LL(1) `M[A,a]` no están solo documentados
aquí: se **calculan programáticamente** en `src/ll1_table.py` con el mismo
algoritmo de punto fijo de `taller_ll1.py`, y `build_table` detecta
conflictos automáticamente. La prueba `tests/test_ll1_table.py::
test_gramatica_sin_conflictos_ll1` falla si algún día la gramática deja de
ser LL(1).

Para verlos impresos:

```bash
python3 -m src.ll1_table
```

##  Arquitectura (Lex → Sintáctica → Semántica → Intérprete)

```
código fuente
   │  src/lexer.py        (Lex)
   ▼
tokens
   │  src/parser.py       (Sintáctica — descenso recursivo LL(1))
   ▼
AST (src/ast_nodes.py)
   │  src/semantic.py     (Semántica)
   ▼
AST verificado
   │  src/interpreter.py  (Ejecución)
   ▼
resultados (print)
```

- **Lex** (`src/lexer.py`): expresiones regulares por tipo de token;
  palabras reservadas (`abs`, `Sin`, `Cos`, `Tan`, `print`) resueltas de
  forma **implícita** (se reconocen primero como identificador y se
  reclasifican contra `KEYWORDS`).
- **Sintáctica** (`src/parser.py`): una función por no terminal, cada rama
  decidida por el conjunto PRED correspondiente — igual al pseudocódigo de
  descenso recursivo de la Clase 5. Construye un AST.
- **Semántica** (`src/semantic.py`): valida que toda variable esté asignada
  antes de usarse, y rechaza división/módulo por la constante literal `0`.
- **Intérprete** (`src/interpreter.py`): evalúa el AST, mantiene la tabla
  de variables y ejecuta `print`.
- **`src/ll1_table.py`**: módulo aparte, solo para la verificación formal
  — calcula PRIMEROS/SIGUIENTES/PRED/tabla y ofrece
  `trace_table_driven(tokens)`, el algoritmo dirigido por tabla (pila +
  `M[A,a]`) de la Clase 5, para reconocer una cadena de forma **totalmente
  independiente** al parser recursivo-descendente (sirve como verificación
  cruzada: si ambos aceptan/rechazan lo mismo, hay más confianza en que el
  parser está bien implementado).

##  Cómo ejecutar

```bash
cd /home/pincho/Documents/Universidad/lenguajes_de_programacion/lenguajes-ll1-calculadora
python3 -m src.main ejemplos/basico.txt
```

Errores (léxico, sintáctico, semántico o de ejecución) se reportan con
línea/columna y detienen la ejecución:

```bash
python3 -m src.main ejemplos/error_sintactico.txt
python3 -m src.main ejemplos/error_semantico.txt
python3 -m src.main ejemplos/division_cero.txt
```

## 8. Pruebas de implementación

```bash
pip install -r requirements.txt   # solo pytest
python3 -m pytest -v
```

Cobertura de las pruebas (`tests/`):

| Archivo | Qué prueba |
|---|---|
| `test_lexer.py` | tokens correctos, palabras reservadas vs. identificadores, números, líneas/columnas, carácter inválido |
| `test_parser.py` | AST correcto, **precedencia** (`+` vs `*`), **asociatividad izquierda** (`10-3-2` = 5, no 9), paréntesis, funciones anidadas, 5 casos de error sintáctico |
| `test_semantic.py` | variable no asignada, uso antes de asignar, división/módulo por cero literal, división por variable (no es error hasta ejecución) |
| `test_interpreter.py` | aritmética, reasignación, funciones trigonométricas, `abs`, división por variable en 0 en tiempo de ejecución, programa completo de `ejemplos/basico.txt` |
| `test_ll1_table.py` | **cero conflictos LL(1)** (prueba formal), PRIMEROS/SIGUIENTES puntuales, `trace_table_driven` acepta programas válidos y rechaza inválidos |

##  Decisiones de diseño

- **Radianes, no grados**, para `Sin/Cos/Tan` — convención de `math` en
  Python; si el enunciado esperara grados, solo hay que envolver
  `math.radians()` en `interpreter.py::FUNCS`.
- **`print(...)` no estaba en el enunciado original**, se agregó porque sin
  alguna forma de observar un resultado no hay manera de probar que el
  intérprete calculó algo — decisión necesaria para la sección de pruebas.
- **División/módulo por cero:** si el divisor es una constante literal
  (`5 / 0`), se detecta en el análisis **semántico** (antes de ejecutar
  nada); si depende de una variable, se detecta en **tiempo de ejecución**,
  porque su valor no se conoce hasta ese momento.
