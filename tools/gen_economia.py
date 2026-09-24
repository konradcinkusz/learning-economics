#!/usr/bin/env python3
"""Genera "Aprendo economía" (main.tex) a partir de content/q*.json:
content/generated-days.tex (una página por día),
content/generated-clave.tex (la clave de respuestas) y
content/generated-diccionario.tex ("Mi diccionario de economía", con la
palabra de cada semana).

Es el generador de "Aprendo los números" (tools/gen_numeros.py, en
https://github.com/konradcinkusz/learning-to-count) para la economía de
cada día: el mismo calendario (260 días, 52 semanas, cuatro trimestres
que son las cuatro estaciones, medalla al final de los tres primeros), y
los temas de "Leo con lupa", el tercer cuaderno de "Aprendo a leer", semana
a semana. Y como allí, lo que se puede comprobar no es una disciplina
editorial: está aquí, y este script falla si algo no cuadra.

Cada día tiene una caja de arriba, "Hoy" (la historia del día, que lee
la niña o el niño, y un dibujo; los lunes, la palabra de la semana), y
una actividad que llena el resto de la página. Las actividades y lo que
se comprueba de cada una están en render_actividad; el porqué, en
notes/01-plan.md.

No editar content/generated-*.tex a mano -- se sobrescriben cada vez que
se ejecuta este script.

Uso:
    python3 tools/gen_economia.py            # regenera content/generated-*.tex
    python3 tools/gen_economia.py --check    # solo valida; exit 1 si algo no
                                             # cuadra o si lo generado está
                                             # desactualizado
"""

import json
import random
import re
import sys
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
SALIDA_DIAS = CONTENT_DIR / "generated-days.tex"
SALIDA_CLAVE = CONTENT_DIR / "generated-clave.tex"
SALIDA_DICCIONARIO = CONTENT_DIR / "generated-diccionario.tex"
LANG_FILE = ROOT / "lang" / "es.tex"

# --------------------------------------------------------------------
# El calendario
# --------------------------------------------------------------------
TOTAL_DIAS = 260
DIAS_POR_SEMANA = 5
SEMANAS_POR_TRIMESTRE = 13
# Mientras el cuaderno se escribe por partes (un PR por trimestre, cada
# uno en verde antes de fusionarse), cuántos días tiene ya escritos: se
# exigen exactamente esos, del 1 en adelante y sin huecos. None = el
# cuaderno está entero, con sus 260 días.
DIAS_ESCRITOS = 10

NOMBRE_MEDALLA = {1: "Otoño", 2: "Invierno", 3: "Primavera"}
ULTIMO_DIA_TRIMESTRE = {1: 65, 2: 130, 3: 195, 4: 260}

# Los temas de cada semana: los de "Leo con lupa" (content/lupa/ en
# "Aprendo a leer"), para que quien lleve los dos cuadernos se encuentre
# la misma semana en los dos. El tema de cada día tiene que ser el de su
# semana.
TEMAS = [
    "La lupa de la abuela", "Un compañero nuevo", "El Club de la Lupa",
    "El caso de las galletas", "Huellas en el cemento", "La hoja de los martes",
    "Ruidos en el desván", "La lista de la compra", "Ocho años",
    "¿Dónde está Luna?", "El museo de los dinosaurios", "La función de Navidad",
    "¡Lector X, descubierto!",
    "Los Reyes que caminan", "Nochebuena y el mapa", "Las doce uvas",
    "El roscón de Reyes", "Un muñeco de nieve madrugador", "El periscopio de Hugo",
    "El Día de la Paz", "El cumpleaños de Papá", "Carnaval", "Una carta del pueblo",
    "Las plantas mustias", "El planetario", "El nido del jardín",
    "Una foto de hace veinticinco años", "Torrijas, esta vez sola",
    "La rueda pinchada", "La entrevista a Paco", "El Día del Libro",
    "El plano antiguo", "Rayo se escapa", "El día de la madre",
    "Dani cumple seis años", "Las abejas del parque", "La granja escuela",
    "¡Aquí está la cápsula!", "La fiesta de fin de curso",
    "La maleta", "Otra vez en el pueblo", "Diez pasos", "El diario de Lucía",
    "Las abejas de Andrés", "La noche de las estrellas fugaces",
    "Una carta de Hugo", "Las fiestas del pueblo", "¡El tesoro de Rosa!",
    "El mapa de Dani y Martín", "Vuelta a la ciudad",
    "Dani, al cole de los mayores", "Vuelta al cole",
]
assert len(TEMAS) == TOTAL_DIAS // DIAS_POR_SEMANA
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes"]

# La historia de cada día la lee la niña o el niño: dos o tres frases,
# que caben en la caja de arriba.
MAX_PALABRAS_HISTORIA = 60


def trimestre_de(semana):
    return (semana - 1) // SEMANAS_POR_TRIMESTRE + 1


# --------------------------------------------------------------------
# La escalera del dinero
# --------------------------------------------------------------------
# Como la de los números en "Aprendo los números": hasta cuánto llega el
# dinero cada trimestre, y con qué monedas y billetes. Sin céntimos: los
# precios del cuaderno son de euros enteros, y las cuentas, las de 2.º.
MAX_EUROS = {1: 20, 2: 50, 3: 100, 4: 100}
MONEDAS = (1, 2)
BILLETES = {1: (5, 10, 20), 2: (5, 10, 20, 50), 3: (5, 10, 20, 50), 4: (5, 10, 20, 50)}

# Las actividades, y la semana en que llega cada una: como con el dinero,
# ninguna se usa antes (ver notes/01-plan.md). Las que no están aquí
# están desde la semana 1.
DESDE_SEMANA = {
    "trueque": 2,   # 1 concha vale 2 cromos
}


class ErrorDeContenido(Exception):
    pass


def escapar(texto):
    """Lo mínimo para que un texto del JSON se pueda poner tal cual en
    LaTeX."""
    return (
        texto.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
        .replace("#", r"\#").replace("_", r"\_")
    )


def campos(dia, actividad, requeridos):
    faltan = [c for c in requeridos if c not in actividad]
    if faltan:
        raise ErrorDeContenido(
            f"día {dia}: a la actividad '{actividad.get('tipo')}' le falta "
            + ", ".join(repr(c) for c in faltan)
        )


def maximo(semana):
    return MAX_EUROS[trimestre_de(semana)]


def comprobar_cantidad(dia, semana, n, que):
    """Una cantidad de cosas o de euros: de 0 al máximo del trimestre."""
    if not isinstance(n, int) or not 0 <= n <= maximo(semana):
        raise ErrorDeContenido(
            f"día {dia}: {que} es {n!r}, y este trimestre las cantidades van del 0 "
            f"al {maximo(semana)} (ver MAX_EUROS)"
        )


# --------------------------------------------------------------------
# Las cosas (diagrams/objetos.tex y diagrams/economia.tex)
# --------------------------------------------------------------------
# macro, singular, plural, género -- el enunciado se compone con ellos
# ("Si 1 concha vale 2 cromos, ¿cuántos cromos te dan por 3 conchas?").
OBJETOS = {
    # Las de este cuaderno (diagrams/economia.tex).
    "lupa": (r"\objLupa", "lupa", "lupas", "f"),
    "cromo": (r"\objCromo", "cromo", "cromos", "m"),
    "canica": (r"\objCanica", "canica", "canicas", "f"),
    "hucha": (r"\objHucha", "hucha", "huchas", "f"),
    # Las de "Aprendo los números" (diagrams/objetos.tex).
    "manzana": (r"\objManzana", "manzana", "manzanas", "f"),
    "pelota": (r"\objPelota", "pelota", "pelotas", "f"),
    "hueso": (r"\objHueso", "hueso", "huesos", "m"),
    "sol": (r"\objSol", "sol", "soles", "m"),
    "toby": (r"\objToby", "perro", "perros", "m"),
    "globo": (r"\objGlobo", "globo", "globos", "m"),
    "estrella": (r"\objEstrella", "estrella", "estrellas", "f"),
    "hoja": (r"\objHoja", "hoja", "hojas", "f"),
    "corazon": (r"\objCorazon", "corazón", "corazones", "m"),
    "caramelo": (r"\objCaramelo", "caramelo", "caramelos", "m"),
    "pez": (r"\objPez", "pez", "peces", "m"),
    "lapiz": (r"\objLapiz", "lápiz", "lápices", "m"),
    "libro": (r"\objLibro", "libro", "libros", "m"),
    "galleta": (r"\objGalleta", "galleta", "galletas", "f"),
    "castana": (r"\objCastana", "castaña", "castañas", "f"),
    "cesta": (r"\objCesta", "cesta", "cestas", "f"),
    "regalo": (r"\objRegalo", "regalo", "regalos", "m"),
    "paraguas": (r"\objParaguas", "paraguas", "paraguas", "m"),
    "arbol": (r"\objArbol", "árbol", "árboles", "m"),
    "coche": (r"\objCoche", "coche", "coches", "m"),
    "trex": (r"\objTrex", "dinosaurio", "dinosaurios", "m"),
    "huevo": (r"\objHuevo", "huevo", "huevos", "m"),
    "gato": (r"\objGato", "gato", "gatos", "m"),
    "mochila": (r"\objMochila", "mochila", "mochilas", "f"),
    "plato": (r"\objPlato", "plato", "platos", "m"),
    "mandarina": (r"\objMandarina", "mandarina", "mandarinas", "f"),
    "osito": (r"\objOsito", "osito", "ositos", "m"),
    "flor": (r"\objFlor", "flor", "flores", "f"),
    "boton": (r"\objBoton", "botón", "botones", "m"),
    "fresa": (r"\objFresa", "fresa", "fresas", "f"),
    "piruleta": (r"\objPiruleta", "piruleta", "piruletas", "f"),
    "ovillo": (r"\objOvillo", "ovillo", "ovillos", "m"),
    "bufanda": (r"\objBufanda", "bufanda", "bufandas", "f"),
    "gorro": (r"\objGorro", "gorro", "gorros", "m"),
    "maceta": (r"\objMaceta", "maceta", "macetas", "f"),
    "bici": (r"\objBici", "bici", "bicis", "f"),
    "tarta": (r"\objTarta", "tarta", "tartas", "f"),
    "abeja": (r"\objAbeja", "abeja", "abejas", "f"),
    "moneda": (r"\objMoneda", "moneda", "monedas", "f"),
    "torrija": (r"\objTorrija", "torrija", "torrijas", "f"),
    "zanahoria": (r"\objZanahoria", "zanahoria", "zanahorias", "f"),
    "tomate": (r"\objTomate", "tomate", "tomates", "m"),
    "pan": (r"\objPan", "pan", "panes", "m"),
    "lechuga": (r"\objLechuga", "lechuga", "lechugas", "f"),
    "maleta": (r"\objMaleta", "maleta", "maletas", "f"),
    "helado": (r"\objHelado", "helado", "helados", "m"),
    "concha": (r"\objConcha", "concha", "conchas", "f"),
    "cubo": (r"\objCubo", "cubo", "cubos", "m"),
    "churro": (r"\objChurro", "churro", "churros", "m"),
    "reloj": (r"\objReloj", "reloj", "relojes", "m"),
}


def nombre_objeto(objeto, n):
    _, singular, plural, _ = OBJETOS[objeto]
    return singular if n == 1 else plural


def femenino(objeto):
    return OBJETOS[objeto][3] == "f"


def comprobar_objeto(dia, objeto):
    if objeto not in OBJETOS:
        raise ErrorDeContenido(
            f"día {dia}: no hay dibujo para «{objeto}» (ver OBJETOS, "
            "diagrams/objetos.tex y diagrams/economia.tex)"
        )


# --------------------------------------------------------------------
# Dibujar cosas
# --------------------------------------------------------------------
# Cada cosa ocupa la caja de -1 a 1 (diagrams/objetos.tex); aquí se
# colocan en unidades de esa caja, y el tikzpicture entero se escala.
def _cosa(macro, x, y):
    return f"\\begin{{scope}}[shift={{({x:.2f},{y:.2f})}}]{macro}\\end{{scope}}"


def fila(objeto, n, escala, por_fila=5, paso=2.4):
    """n cosas en filas de `por_fila`, centradas."""
    macro = OBJETOS[objeto][0]
    piezas = []
    filas = [min(por_fila, n - i) for i in range(0, n, por_fila)]
    for f, cuantas in enumerate(filas):
        for i in range(cuantas):
            piezas.append(_cosa(macro, (i - (cuantas - 1) / 2) * paso, -f * paso))
    return (
        f"\\begin{{tikzpicture}}[objeto, scale={escala}, baseline=(current bounding box.center)]"
        + "".join(piezas) + "\\end{tikzpicture}"
    )


# --------------------------------------------------------------------
# Las plantillas
# --------------------------------------------------------------------
PLANTILLA_DIA = Template(r"""\begin{diapagina}{$dia}{$semana}{$trimestre}{$tema}
\hoy{$dibujo}{$historia}{$palabra}
$actividad
\end{diapagina}
""")

# Un enunciado, la instrucción y un dibujo, centrado en el hueco.
PLANTILLA_CAJA = Template(r"""\begin{$caja}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
$dibujo
\end{center}
\end{$caja}""")

# Lo mismo, y debajo lo que se completa: \huecoRespuesta es el hueco.
PLANTILLA_CON_RESPUESTA = Template(r"""\begin{$caja}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
$dibujo

\vspace{12mm}
{\fontsize{34}{40}\selectfont\bfseries $respuesta}
\end{center}
\end{$caja}""")

PLANTILLA_VF = Template(r"""\begin{cajaVF}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
$frases
\end{cajaVF}""")

PLANTILLA_DIBUJA = Template(r"""\begin{cajaDibuja}
\enunciado{$enunciado}
\end{cajaDibuja}""")

PLANTILLA_REPASA = Template(r"""\begin{cajaRepasa}[abajo]
{\large\textbf{\color{colorCrea}\lblPalabraSemana:} \textbf{$palabra}. $definicion\par}
\vspace{3mm}
\begin{listaRepaso}
$items
\end{listaRepaso}
\vspace{2mm}
\enunciado{$prompt}
\tcblower
$cartel
\end{cajaRepasa}""")

PLANTILLA_MEDALLA = Template(r"""\begin{center}
\vspace*{3cm}
\medalla{$dia}

\vspace{10mm}
{\fontsize{34}{40}\selectfont\bfseries\color{colorLectura}\lblMedalla{$estacion}}\\[8mm]
{\Large $dia\ días, $dia\ páginas.}\\[12mm]
{\Large \lblMedallaAnimo}
\end{center}
\vspace*{\fill}
\newpage
""")

def enumerar(cosas, frases=False):
    """"un paraguas, una cuchara y una escoba"; si son frases enteras,
    cada una entre comillas y separadas por barras: «...» / «...»."""
    cosas = [c.rstrip(".") for c in cosas]
    if frases:
        return " / ".join(f"«{c}»" for c in cosas)
    return ", ".join(cosas[:-1]) + " y " + cosas[-1]


ORDINALES = {1: "la primera", 2: "la segunda", 3: "la tercera", 4: "la cuarta", 5: "la quinta"}
FUENTE_TEXTO = r"\large"


# --------------------------------------------------------------------
# Los dibujos de las actividades
# --------------------------------------------------------------------
def dibujo_clasifica(cajas, cosas):
    """Las cosas, en tarjetas, arriba (de tres en tres), cada una con su
    punto debajo; las dos cajas, abajo, cada una con su nombre: de cada
    punto se traza una línea hasta su caja. Con textos largos, la letra
    de las tarjetas, más pequeña. En cm."""
    por_fila, ancho, alto, hueco = 3, 4.8, 2.0, 0.35
    largo = max(len(c[0]) for c in cosas)
    fuente = r"\Large" if largo <= 18 else r"\large" if largo <= 30 else r"\normalsize"
    piezas = []
    filas = [cosas[i:i + por_fila] for i in range(0, len(cosas), por_fila)]
    for f, fila_cosas in enumerate(filas):
        x0 = -(len(fila_cosas) * ancho + (len(fila_cosas) - 1) * hueco) / 2
        y = -f * (alto + 0.9)
        for i, (texto, _) in enumerate(fila_cosas):
            x = x0 + i * (ancho + hueco) + ancho / 2
            piezas.append(
                f"\\node[draw, line width=1pt, rounded corners=2mm, fill=white, minimum width={ancho}cm, "
                f"minimum height={alto}cm, text width={ancho - 0.4:.2f}cm, align=center, "
                f"font={fuente}, execute at begin node=\\sinCortes] at ({x:.2f},{y:.2f}) {{{escapar(texto)}}};"
                f"\\fill ({x:.2f},{y - alto / 2 - 0.3:.2f}) circle (1.3mm);"
            )
    y_cajas = -len(filas) * (alto + 0.9) - 2.4
    for i, nombre in enumerate(cajas):
        x = (-1 if i == 0 else 1) * 3.9
        piezas.append(
            f"\\draw[line width=1.4pt, rounded corners=3mm, fill=white] ({x - 3.5:.2f},{y_cajas - 3.4:.2f}) "
            f"rectangle ({x + 3.5:.2f},{y_cajas:.2f});"
            f"\\node[font=\\Large\\bfseries, text width=6.6cm, align=center, execute at begin node=\\sinCortes] at ({x:.2f},{y_cajas - 0.75:.2f}) "
            f"{{{escapar(nombre)}}};"
        )
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_une(izquierda, derecha):
    """Dos columnas de textos, cada uno con su punto: los de la izquierda
    a su derecha, los de la derecha a su izquierda. En cm."""
    fila_alto, x_punto, hueco = 2.3, 0.0, 3.2
    piezas = []
    for i, (a, b) in enumerate(zip(izquierda, derecha)):
        y = -i * fila_alto
        piezas.append(
            f"\\node[anchor=east, text width=5.2cm, align=right, font=\\Large, execute at begin node=\\sinCortes] at ({x_punto - 0.3:.2f},{y:.2f}) "
            f"{{{escapar(a)}}};"
            f"\\fill ({x_punto:.2f},{y:.2f}) circle (1.3mm);"
            f"\\fill ({x_punto + hueco:.2f},{y:.2f}) circle (1.3mm);"
            f"\\node[anchor=west, text width=5.2cm, align=left, font=\\Large, execute at begin node=\\sinCortes] at ({x_punto + hueco + 0.3:.2f},{y:.2f}) "
            f"{{{escapar(b)}}};"
        )
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def cosas_en_fila(objeto, n, escala):
    """n cosas en fila (en dos si son más de seis), para "Trueque"."""
    return fila(objeto, n, escala, por_fila=6 if n <= 6 else -(-n // 2))


def dibujo_trueque(a, na, b, nb, preg, n, otra):
    """Arriba, lo que vale lo que: na cosas a = nb cosas b; abajo, n cosas
    de `preg` = el hueco, y una de `otra` al lado, para que se vea qué se
    cuenta. Todas las cosas a la misma escala, la mayor con la que cabe
    todo en el ancho de la caja. En cm."""
    def ancho_col(ns, s):
        return max(min(k, 6 if k <= 6 else -(-k // 2)) * 2.4 * s for k in ns)
    # A la izquierda, las na cosas de arriba y las n de abajo; a la
    # derecha, las nb de arriba, y el hueco (2,6 cm) con su cosa al lado.
    escala = 0.8
    while escala > 0.3 and (ancho_col([na, n], escala) + 2.2
                            + max(ancho_col([nb], escala), 2.9 + 2.4 * escala)) > 14.0:
        escala = round(escala - 0.02, 2)
    igual = r"{\fontsize{40}{40}\selectfont\bfseries =}"
    return (
        "\\begin{tabular}{@{}c@{\\hspace{8mm}}c@{\\hspace{8mm}}c@{}}\n"
        f"{cosas_en_fila(a, na, escala)} & {igual} & {cosas_en_fila(b, nb, escala)} \\\\[14mm]\n"
        f"{cosas_en_fila(preg, n, escala)} & {igual} & "
        f"\\huecoRespuesta\\hspace{{3mm}}{cosas_en_fila(otra, 1, escala)} \\\\\n"
        "\\end{tabular}"
    )


# --------------------------------------------------------------------
# Actividades
# --------------------------------------------------------------------
def render_actividad(d):
    """(tex, clave): la caja de la actividad del día, y su entrada de la
    clave de respuestas (None si no tiene nada que comprobar)."""
    num, semana, a = d["dia"], d["semana"], d["actividad"]
    tipo = a.get("tipo")
    if tipo in DESDE_SEMANA and semana < DESDE_SEMANA[tipo]:
        raise ErrorDeContenido(
            f"día {num}: '{tipo}' no llega hasta la semana {DESDE_SEMANA[tipo]} (ver DESDE_SEMANA)"
        )

    if tipo == "clasifica":
        campos(num, a, ["cajas", "cosas"])
        cajas, cosas = a["cajas"], a["cosas"]
        if len(cajas) != 2 or not all(isinstance(c, str) and c for c in cajas):
            raise ErrorDeContenido(f"día {num}: 'clasifica' lleva dos cajas, con su nombre ({cajas})")
        if not 4 <= len(cosas) <= 6:
            raise ErrorDeContenido(f"día {num}: 'clasifica' lleva de 4 a 6 cosas ({len(cosas)})")
        for c in cosas:
            if len(c) != 2 or c[1] not in (0, 1):
                raise ErrorDeContenido(f"día {num}: cada cosa de 'clasifica' es [texto, 0 o 1] ({c})")
        if len({c[0] for c in cosas}) != len(cosas):
            raise ErrorDeContenido(f"día {num}: en 'clasifica', una cosa sale dos veces")
        for i in (0, 1):
            if sum(1 for c in cosas if c[1] == i) < 2:
                raise ErrorDeContenido(f"día {num}: en 'clasifica', cada caja tiene al menos dos cosas")
        # Las cosas, mezcladas: el mismo JSON da siempre la misma página.
        # Que no vayan todas las de una caja seguidas: de una caja a la
        # otra, al menos dos veces.
        rng, orden = random.Random(num), list(cosas)
        while sum(orden[i][1] != orden[i + 1][1] for i in range(len(orden) - 1)) < 2:
            rng.shuffle(orden)
        # Tarjetas con frases enteras (empiezan en mayúscula), entre comillas.
        frases = any(c[0][0].isupper() or "," in c[0] for c in cosas)
        clave = " ".join(f"{cajas[i]}: {enumerar([c[0] for c in cosas if c[1] == i], frases)}." for i in (0, 1))
        return PLANTILLA_CAJA.substitute(
            caja="cajaClasifica",
            enunciado=escapar(a.get("pregunta", "Une cada cosa con su caja.")),
            instruccion="Lee cada tarjeta, y traza una línea desde su punto hasta la caja que le toca.",
            dibujo=dibujo_clasifica(cajas, orden),
        ), ("clasifica", clave)

    if tipo == "une":
        campos(num, a, ["pares"])
        pares = a["pares"]
        if not 3 <= len(pares) <= 5 or any(len(p) != 2 for p in pares):
            raise ErrorDeContenido(f"día {num}: 'une' lleva de 3 a 5 parejas ({pares})")
        for lado in (0, 1):
            if len({p[lado] for p in pares}) != len(pares):
                raise ErrorDeContenido(f"día {num}: en 'une', una cosa sale dos veces")
        # La columna de la derecha, desordenada: ninguna enfrente de la
        # suya. La baraja el número del día, así que siempre sale igual.
        rng, derecha = random.Random(num), [p[1] for p in pares]
        while any(x == p[1] for x, p in zip(derecha, pares)):
            rng.shuffle(derecha)
        return PLANTILLA_CAJA.substitute(
            caja="cajaUne",
            enunciado=escapar(a.get("pregunta", "Une cada una con la suya.")),
            instruccion="Lee las dos columnas, y traza una línea desde cada punto de la izquierda "
                        "hasta el punto de la derecha que le toca.",
            dibujo=dibujo_une([p[0] for p in pares], derecha),
        ), ("une", "; ".join(f"{p[0]} → {p[1]}" for p in pares))

    if tipo == "vf":
        campos(num, a, ["frases"])
        frases = a["frases"]
        if not 3 <= len(frases) <= 5 or any(len(f) != 2 or not isinstance(f[1], bool) for f in frases):
            raise ErrorDeContenido(f"día {num}: 'vf' lleva de 3 a 5 frases, cada una [texto, true o false]")
        if len({f[1] for f in frases}) != 2:
            raise ErrorDeContenido(f"día {num}: en 'vf' hay alguna verdad y alguna mentira")
        return PLANTILLA_VF.substitute(
            enunciado=escapar(a.get("pregunta", "¿Es verdad o es mentira?")),
            instruccion="Lee cada frase, y rodea la V si es verdad, o la F si es mentira (falso).",
            frases="\n".join(f"\\frasevf{{{i}}}{{{escapar(f[0])}}}" for i, f in enumerate(frases, 1)),
        ), ("vf", ", ".join(f"{i}: {'V' if f[1] else 'F'}" for i, f in enumerate(frases, 1)))

    if tipo == "trueque":
        # "cambio": [cosa, cuántas, otra cosa, cuántas]: tantas de una
        # valen tantas de la otra. "pregunta": [cosa, cuántas]: ¿cuántas de
        # la otra te dan por esas?
        campos(num, a, ["cambio", "pregunta"])
        oa, na, ob, nb = a["cambio"]
        op, n = a["pregunta"]
        for o in (oa, ob, op):
            comprobar_objeto(num, o)
        if oa == ob or op not in (oa, ob):
            raise ErrorDeContenido(f"día {num}: en 'trueque' se cambian dos cosas distintas, y se pregunta por una de ellas")
        for x, que in ((na, "lo que se cambia"), (nb, "lo que se cambia"), (n, "lo que se pregunta")):
            if not isinstance(x, int) or x < 1:
                raise ErrorDeContenido(f"día {num}: en 'trueque', {que} es 1 o más ({x!r})")
            comprobar_cantidad(num, semana, x, f"en 'trueque', {que}")
        de, otra, nde, notra = (oa, ob, na, nb) if op == oa else (ob, oa, nb, na)
        if (n * notra) % nde:
            raise ErrorDeContenido(f"día {num}: en 'trueque', {n} {nombre_objeto(de, n)} no se cambian justo")
        respuesta = n * notra // nde
        comprobar_cantidad(num, semana, respuesta, "en 'trueque', la respuesta")
        if n == nde:
            raise ErrorDeContenido(f"día {num}: en 'trueque', la pregunta no puede ser el mismo cambio de arriba")
        vale = lambda k: "vale" if k == 1 else "valen"
        cuantas = "cuántas" if femenino(otra) else "cuántos"
        enunciado = (f"Si {na} {nombre_objeto(oa, na)} {vale(na)} {nb} {nombre_objeto(ob, nb)}, "
                     f"¿{cuantas} {nombre_objeto(otra, 2)} te dan por {n} {nombre_objeto(de, n)}?")
        return PLANTILLA_CAJA.substitute(
            caja="cajaTrueque",
            enunciado=enunciado,
            instruccion="Mira el cambio de arriba. Si hace falta, dibuja las cosas, y escribe "
                        "en el hueco cuántas te dan.",
            dibujo=dibujo_trueque(oa, na, ob, nb, de, n, otra),
        ), ("trueque", f"{respuesta} {nombre_objeto(otra, respuesta)}")

    if tipo == "dibuja":
        campos(num, a, ["prompt"])
        return PLANTILLA_DIBUJA.substitute(enunciado=escapar(a["prompt"])), None

    if tipo == "repasa":
        campos(num, a, ["checklist", "prompt"])
        if len(a["checklist"]) != 3:
            raise ErrorDeContenido(f"día {num}: 'repasa' lleva tres cosas que marcar")
        palabra = d["palabra_semana"]
        cartel = f"\\cartel{{\\lblPaginasHechas{{{num}}}}}" if num % 10 == 0 else ""
        return PLANTILLA_REPASA.substitute(
            palabra=escapar(palabra["palabra"].capitalize()),
            definicion=escapar(palabra["definicion"]),
            items="\n".join(f"\\item {escapar(i)}" for i in a["checklist"]),
            prompt=escapar(a["prompt"]), cartel=cartel,
        ), None

    raise ErrorDeContenido(f"día {num}: tipo de actividad desconocido: {tipo!r}")


# --------------------------------------------------------------------
# Cargar y validar
# --------------------------------------------------------------------
def cargar():
    dias, semanas = [], {}
    for ruta in sorted(CONTENT_DIR.glob("q*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        dias += datos["dias"]
        for s in datos.get("semanas", []):
            if s.get("semana") in semanas:
                raise ErrorDeContenido(f"la semana {s.get('semana')} está dos veces en 'semanas'")
            semanas[s.get("semana")] = s
    return sorted(dias, key=lambda d: d["dia"]), semanas


def validar_semanas(semanas, total_semanas):
    """Cada semana tiene su palabra: la palabra, lo que quiere decir, y
    las formas en que puede salir en la historia del lunes. Ninguna se
    repite."""
    if sorted(semanas) != list(range(1, total_semanas + 1)):
        raise ErrorDeContenido(
            f"'semanas' tiene que tener las semanas del 1 al {total_semanas}, sin huecos"
        )
    vistas = {}
    for n, s in sorted(semanas.items()):
        for c in ("palabra", "definicion", "formas"):
            if not s.get(c):
                raise ErrorDeContenido(f"semana {n}: falta '{c}'")
        palabra = s["palabra"]
        if palabra != palabra.lower():
            raise ErrorDeContenido(f"semana {n}: la palabra va en minúsculas («{palabra}»)")
        if palabra in vistas:
            raise ErrorDeContenido(f"semana {n}: la palabra «{palabra}» ya es la de la semana {vistas[palabra]}")
        vistas[palabra] = n
        if palabra not in s["formas"]:
            raise ErrorDeContenido(f"semana {n}: la palabra «{palabra}» tiene que estar entre sus formas")
        d = s["definicion"]
        if not d[0].isupper() or not d.endswith("."):
            raise ErrorDeContenido(f"semana {n}: la definición empieza en mayúscula y termina en punto («{d}»)")


def dice(texto, formas):
    t = texto.lower()
    return any(re.search(rf"(?<!\w){re.escape(f)}(?!\w)", t) for f in formas)


def validar_dias(dias, semanas):
    total = DIAS_ESCRITOS or TOTAL_DIAS
    numeros = [d["dia"] for d in dias]
    if numeros != list(range(1, total + 1)):
        raise ErrorDeContenido(
            f"tienen que estar los días del 1 al {total}, sin huecos ni repetidos"
            + (" (en obras: DIAS_ESCRITOS)" if DIAS_ESCRITOS else "")
        )
    if total % DIAS_POR_SEMANA:
        raise ErrorDeContenido("los días escritos son semanas enteras (DIAS_ESCRITOS)")
    validar_semanas(semanas, total // DIAS_POR_SEMANA)
    for d in dias:
        num = d["dia"]
        semana = (num - 1) // DIAS_POR_SEMANA + 1
        dia_semana = (num - 1) % DIAS_POR_SEMANA
        if d.get("semana") != semana:
            raise ErrorDeContenido(f"día {num}: es de la semana {semana}, no {d.get('semana')}")
        if d.get("tema") != TEMAS[semana - 1]:
            raise ErrorDeContenido(
                f"día {num}: el tema de la semana {semana} es «{TEMAS[semana - 1]}», "
                f"no «{d.get('tema')}»"
            )
        for c in ("objeto", "historia", "actividad"):
            if c not in d:
                raise ErrorDeContenido(f"día {num}: falta '{c}'")
        comprobar_objeto(num, d["objeto"])
        palabras = len(d["historia"].split())
        if palabras > MAX_PALABRAS_HISTORIA:
            raise ErrorDeContenido(
                f"día {num}: la historia tiene {palabras} palabras, y caben {MAX_PALABRAS_HISTORIA}"
            )
        # El lunes, la historia dice la palabra de la semana.
        palabra = semanas[semana]
        if dia_semana == 0 and not dice(d["historia"], palabra["formas"]):
            raise ErrorDeContenido(
                f"día {num}: la historia del lunes dice la palabra de la semana "
                f"({' / '.join(palabra['formas'])}): «{d['historia']}»"
            )
        tipo = d["actividad"].get("tipo")
        if (dia_semana == DIAS_POR_SEMANA - 1) != (tipo == "repasa"):
            raise ErrorDeContenido(
                f"día {num}: 'repasa' es la actividad de los viernes, y solo de los viernes"
            )


# --------------------------------------------------------------------
# Generar
# --------------------------------------------------------------------
CABECERA = (
    "% {nombre}\n"
    "% GENERADO por tools/gen_economia.py a partir de content/q*.json.\n"
    "% NO EDITAR A MANO -- los cambios se perderán en la siguiente\n"
    "% ejecución de `make generate`. Edita content/q*.json en su lugar.\n\n"
)


def generar(dias, semanas):
    piezas = [CABECERA.format(nombre="content/generated-days.tex")]
    claves = [CABECERA.format(nombre="content/generated-clave.tex")]
    for d in dias:
        num, semana = d["dia"], d["semana"]
        trimestre = trimestre_de(semana)
        palabra = semanas[semana]
        d = dict(d, palabra_semana=palabra)
        actividad, clave = render_actividad(d)
        es_lunes = (num - 1) % DIAS_POR_SEMANA == 0
        piezas.append(PLANTILLA_DIA.substitute(
            dia=num, semana=semana, trimestre=trimestre,
            tema=escapar(d["tema"]),
            dibujo=fila(d["objeto"], 1, escala=1.15),
            historia=escapar(d["historia"]),
            palabra=(f"\\palabraSemana{{{escapar(palabra['palabra'])}}}{{{escapar(palabra['definicion'])}}}"
                     if es_lunes else ""),
            actividad=actividad,
        ))
        if clave:
            etiqueta, texto = clave
            claves.append(f"\\claveEntrada{{{num}}}{{\\lbl{etiqueta.capitalize() if etiqueta != 'vf' else 'VF'}}}"
                          f"{{{escapar(texto)}}}\n")
        if num == ULTIMO_DIA_TRIMESTRE.get(trimestre) and trimestre in NOMBRE_MEDALLA:
            piezas.append(PLANTILLA_MEDALLA.substitute(dia=num, estacion=NOMBRE_MEDALLA[trimestre]))
    # "Mi diccionario de economía": las palabras de las semanas, por orden
    # alfabético (sin tildes para ordenar: "ahorro" antes que "árbol").
    orden = sorted(semanas.values(), key=lambda s: s["palabra"].translate(str.maketrans("áéíóúü", "aeiouu")))
    diccionario = CABECERA.format(nombre="content/generated-diccionario.tex") + "".join(
        f"\\entradaDiccionario{{{escapar(s['palabra'].capitalize())}}}{{{escapar(s['definicion'])}}}{{{s['semana']}}}\n"
        for s in orden)
    return "\n".join(piezas), "".join(claves), diccionario


def comprobar_totaldias():
    """lang/es.tex promete los mismos 260 días que este script."""
    m = re.search(r"\\newcommand\{\\totaldias\}\{(\d+)\}", LANG_FILE.read_text(encoding="utf-8"))
    if not m or int(m.group(1)) != TOTAL_DIAS:
        raise ErrorDeContenido(f"\\totaldias en lang/es.tex tiene que ser {TOTAL_DIAS}")


def main():
    check_only = "--check" in sys.argv
    try:
        comprobar_totaldias()
        dias, semanas = cargar()
        validar_dias(dias, semanas)
        tex, clave, diccionario = generar(dias, semanas)
    except ErrorDeContenido as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    salidas = [(SALIDA_DIAS, tex), (SALIDA_CLAVE, clave), (SALIDA_DICCIONARIO, diccionario)]
    if check_only:
        for ruta, contenido in salidas:
            actual = ruta.read_text(encoding="utf-8") if ruta.exists() else None
            if actual != contenido:
                print(
                    f"DESACTUALIZADO: {ruta.relative_to(ROOT)} no coincide con "
                    "content/q*.json -- ejecuta `make generate`.",
                    file=sys.stderr,
                )
                return 1
        obras = f" (en obras: {len(dias)} de {TOTAL_DIAS} días escritos)" if DIAS_ESCRITOS else ""
        print(f"OK: {len(dias)} días validados{obras}, y lo generado, al día.")
        return 0

    for ruta, contenido in salidas:
        ruta.write_text(contenido, encoding="utf-8")
    print(f"Escritos los {len(dias)} días, la clave y el diccionario.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
