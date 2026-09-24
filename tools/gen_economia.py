#!/usr/bin/env python3
"""Genera "Aprendo economía" (main.tex) a partir de content/q*.json:
content/generated-days.tex (una página por día),
content/generated-clave.tex (la clave de respuestas) y
content/generated-diccionario.tex ("Mi diccionario de economía", con la
palabra de cada semana); y el mismo cuaderno en otras lenguas, página a
página: "First Economics" (english.tex), en inglés, en content/english/,
y "Poznaję ekonomię" (polish.tex), en polaco, en content/polish/ (los
mismos tres ficheros).

Las traducciones no tienen días propios: cada uno es el de "Aprendo
economía" -- el mismo número, el mismo dibujo, la misma actividad, con
las mismas cosas, los mismos precios y las mismas respuestas --, con la
historia, el tema y los textos de su actividad en su lengua, y con sus
palabras de la semana, que están en content/<lengua>/q*.json
(cargar_traduccion, más abajo). Todo lo que se escribe en la página en
una lengua o en otra sale de tools/idiomas.py, y las comprobaciones son
las mismas para todos los cuadernos.

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

No editar content/generated-*.tex, content/english/generated-*.tex ni
content/polish/generated-*.tex a mano -- se sobrescriben cada vez que se
ejecuta este script.

Uso:
    python3 tools/gen_economia.py            # regenera los tres cuadernos
    python3 tools/gen_economia.py --check    # solo valida; exit 1 si algo no
                                             # cuadra o si lo generado está
                                             # desactualizado
"""

import itertools
import json
import random
import re
import sys
from pathlib import Path
from string import Template

from idiomas import ESPANOL, INGLES, POLACO

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"

# --------------------------------------------------------------------
# El calendario
# --------------------------------------------------------------------
TOTAL_DIAS = 260
DIAS_POR_SEMANA = 5
SEMANAS_POR_TRIMESTRE = 13
# Mientras el cuaderno se escribe por partes (un PR por trimestre, cada
# uno en verde antes de fusionarse), cuántos días tiene ya escritos: se
# exigen exactamente esos, del 1 en adelante y sin huecos. None = el
# cuaderno está entero, con sus 260 días. DIAS_ESCRITOS_INGLES y
# DIAS_ESCRITOS_POLACO, lo mismo para "First Economics" y "Poznaję
# ekonomię", que se escriben también por partes: sus días son los
# primeros de "Aprendo economía".
DIAS_ESCRITOS = None
DIAS_ESCRITOS_INGLES = None
DIAS_ESCRITOS_POLACO = None


# Los cuadernos: su lengua, dónde están sus textos (y lo que generan), el
# fichero de sus cadenas de texto (que promete los mismos 260 días que
# este script) y cuántos días tienen escritos.
class Cuaderno:
    def __init__(self, nombre, lengua, carpeta, lang, escritos, constante):
        self.nombre, self.lengua, self.carpeta = nombre, lengua, carpeta
        self.escritos, self.constante = escritos, constante
        self.salida_dias = carpeta / "generated-days.tex"
        self.salida_clave = carpeta / "generated-clave.tex"
        self.salida_diccionario = carpeta / "generated-diccionario.tex"
        self.lang = ROOT / "lang" / lang


APRENDO = Cuaderno("Aprendo economía", ESPANOL, CONTENT_DIR, "es.tex", DIAS_ESCRITOS, "DIAS_ESCRITOS")
# Las traducciones de "Aprendo economía", página a página.
TRADUCCIONES = (
    Cuaderno("First Economics", INGLES, CONTENT_DIR / "english", "en.tex",
             DIAS_ESCRITOS_INGLES, "DIAS_ESCRITOS_INGLES"),
    Cuaderno("Poznaję ekonomię", POLACO, CONTENT_DIR / "polish", "pl.tex",
             DIAS_ESCRITOS_POLACO, "DIAS_ESCRITOS_POLACO"),
)

ULTIMO_DIA_TRIMESTRE = {1: 65, 2: 130, 3: 195, 4: 260}

# Los temas de cada semana (los de "Leo con lupa") y el nombre de cada
# medalla están en tools/idiomas.py, en todas las lenguas.
for _lengua in (ESPANOL, INGLES, POLACO):
    assert len(_lengua.temas) == TOTAL_DIAS // DIAS_POR_SEMANA

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
    "dinero": 3,    # contar monedas y billetes: la semana del dinero
    "reparte": 4,   # la escasez: repartir, y lo que sobra
    "compra": 8,    # la lista de la compra: sumar precios
    "problema": 8,
    "botes": 9,     # el ahorro: ahorrar, gastar y compartir
    "hucha": 9,
    "llega": 11,    # el precio: ¿me llega?, y la vuelta
    "cambio": 11,
    "ordena": 12,   # el equipo: primero esto, después aquello
    "elige": 14,    # elegir: no se puede tener todo
    "compara": 16,  # el kilo: la misma fruta, en dos tiendas
    "cuentas": 28,  # el gasto: lo que entra, lo que sale y lo que queda
}


# Lo que se come: al repartirlo, va en platos; lo demás, en recuadros.
COMIDA = {"manzana", "caramelo", "galleta", "castana", "huevo", "mandarina", "fresa", "piruleta",
          "tarta", "torrija", "zanahoria", "tomate", "pan", "lechuga", "helado", "churro",
          "uva", "racimo", "roscon", "leche", "miel", "limon"}


class ErrorDeContenido(Exception):
    pass


def escapar(texto):
    """Lo mínimo para que un texto del JSON se pueda poner tal cual en
    LaTeX; y el número y su € nunca se separan al final de una línea
    ("5~€")."""
    return re.sub(r"(\d) €", r"\1~€", (
        texto.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
        .replace("#", r"\#").replace("_", r"\_")
    ))


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


def comprobar_dinero(dia, semana, valores, que):
    """Unas monedas y unos billetes: que existan este trimestre, y que
    todo junto no pase del máximo."""
    validos = set(MONEDAS) | set(BILLETES[trimestre_de(semana)])
    if not valores or any(v not in validos for v in valores):
        raise ErrorDeContenido(
            f"día {dia}: {que} son monedas de 1 y 2 € y billetes de "
            f"{ESPANOL.enumerar([str(b) for b in BILLETES[trimestre_de(semana)]])} € este trimestre ({valores})"
        )
    comprobar_cantidad(dia, semana, sum(valores), f"{que}, todo junto,")


# --------------------------------------------------------------------
# Las cosas (diagrams/objetos.tex y diagrams/economia.tex)
# --------------------------------------------------------------------
# El dibujo de cada una; cómo se llama, en cada lengua, está en
# tools/idiomas.py (el enunciado se compone con su nombre: "Si 1 concha
# vale 2 cromos, ¿cuántos cromos te dan por 3 conchas?").
OBJETOS = {
    # Las de este cuaderno (diagrams/economia.tex).
    "lupa": r"\objLupa",
    "cromo": r"\objCromo",
    "canica": r"\objCanica",
    "hucha": r"\objHucha",
    "entrada": r"\objEntrada",
    "uva": r"\objUva",
    "racimo": r"\objRacimo",
    "roscon": r"\objRoscon",
    "carta": r"\objCarta",
    "telescopio": r"\objTelescopio",
    "antifaz": r"\objAntifaz",
    "mapa": r"\objMapa",
    "leche": r"\objLeche",
    "miel": r"\objMiel",
    "tortuga": r"\objTortuga",
    "limon": r"\objLimon",
    "caracol": r"\objCaracol",
    # Las de "Aprendo los números" (diagrams/objetos.tex).
    "manzana": r"\objManzana",
    "pelota": r"\objPelota",
    "hueso": r"\objHueso",
    "sol": r"\objSol",
    "toby": r"\objToby",
    "huella": r"\objHuella",
    "globo": r"\objGlobo",
    "estrella": r"\objEstrella",
    "hoja": r"\objHoja",
    "corazon": r"\objCorazon",
    "caramelo": r"\objCaramelo",
    "pez": r"\objPez",
    "lapiz": r"\objLapiz",
    "libro": r"\objLibro",
    "galleta": r"\objGalleta",
    "castana": r"\objCastana",
    "cesta": r"\objCesta",
    "regalo": r"\objRegalo",
    "paraguas": r"\objParaguas",
    "arbol": r"\objArbol",
    "coche": r"\objCoche",
    "trex": r"\objTrex",
    "huevo": r"\objHuevo",
    "gato": r"\objGato",
    "mochila": r"\objMochila",
    "plato": r"\objPlato",
    "mandarina": r"\objMandarina",
    "osito": r"\objOsito",
    "flor": r"\objFlor",
    "boton": r"\objBoton",
    "fresa": r"\objFresa",
    "piruleta": r"\objPiruleta",
    "ovillo": r"\objOvillo",
    "bufanda": r"\objBufanda",
    "gorro": r"\objGorro",
    "maceta": r"\objMaceta",
    "bici": r"\objBici",
    "tarta": r"\objTarta",
    "abeja": r"\objAbeja",
    "moneda": r"\objMoneda",
    "torrija": r"\objTorrija",
    "zanahoria": r"\objZanahoria",
    "tomate": r"\objTomate",
    "pan": r"\objPan",
    "lechuga": r"\objLechuga",
    "maleta": r"\objMaleta",
    "helado": r"\objHelado",
    "concha": r"\objConcha",
    "cubo": r"\objCubo",
    "churro": r"\objChurro",
    "corona": r"\objCorona",
    "muneco": r"\objMuneco",
    "pajaro": r"\objPajaro",
    "paloma": r"\objPaloma",
    "vela": r"\objVela",
    "reloj": r"\objReloj",
    "regadera": r"\objRegadera",
    "rueda": r"\objRueda",
    "cometa": r"\objCometa",
    "copo": r"\objCopo",
    "tarjeta": r"\objTarjeta",
    "nube": r"\objNube",
    "gota": r"\objGota",
    "rosa": r"\objRosa",
    "brote": r"\objBrote",
    "pollito": r"\objPollito",
    "mano": r"\objMano",
    "gorrofiesta": r"\objGorroFiesta",
}
# Cada cosa que se puede dibujar tiene su nombre en todas las lenguas.
for _lengua in (ESPANOL, INGLES, POLACO):
    assert set(_lengua.objetos) == set(OBJETOS), set(_lengua.objetos) ^ set(OBJETOS)


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
    macro = OBJETOS[objeto]
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
\sinPartir
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

# La página de medalla del final de cada trimestre está en
# tools/idiomas.py (plantilla_medalla), en todas las lenguas.

SIGNOS = {"+": "+", "-": "−"}      # el menos de verdad (U+2212), el de Andika


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


def dibujo_dinero(valores):
    """Los billetes, primero, y después las monedas, en fila (en dos si no
    caben). En cm."""
    piezas = []
    orden = sorted(valores, reverse=True)
    anchos = [3.6 if v >= 5 else 2.2 for v in orden]
    filas, fila_d, ancho_fila = [], [], 0.0
    for v, w in zip(orden, anchos):
        if fila_d and ancho_fila + w > 14.5:
            filas.append(fila_d)
            fila_d, ancho_fila = [], 0.0
        fila_d.append((v, w))
        ancho_fila += w
    filas.append(fila_d)
    for f, fila_d in enumerate(filas):
        x = -sum(w for _, w in fila_d) / 2
        for v, w in fila_d:
            macro = f"\\billete{{{v}}}" if v >= 5 else f"\\monedaEuro{{{v}}}"
            piezas.append(f"\\begin{{scope}}[shift={{({x + w / 2:.2f},{-f * 2.3:.2f})}}]{macro}\\end{{scope}}")
            x += w
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def etiqueta(precio):
    """La etiqueta de un precio: más ancha si el precio tiene dos cifras."""
    return f"\\etiqueta[{0.3 if precio >= 10 else 0}]{{{precio}}}"


def dibujo_precios(cosas, escala=1.1):
    """Cosas en fila, cada una con su etiqueta de precio debajo. En las
    unidades de las cosas (una caja de 2 x 2), a `escala`."""
    paso = 3.0
    piezas = []
    for i, (objeto, precio) in enumerate(cosas):
        x = (i - (len(cosas) - 1) / 2) * paso
        piezas.append(_cosa(OBJETOS[objeto], x, 0.35))
        piezas.append(f"\\begin{{scope}}[shift={{({x:.2f},-1.25)}}, transform shape]{etiqueta(precio)}\\end{{scope}}")
    return f"\\begin{{tikzpicture}}[objeto, scale={escala}]\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_reparte(objeto, total, entre):
    """Las cosas, arriba, en filas de cinco; abajo, vacío, un plato por
    cada uno si es comida, o un recuadro si no (una estantería, una
    camisa...), para dibujar lo que le toca. En cm."""
    cosas = fila(objeto, total, escala=round(min(0.55, 11.0 / (min(total, 5) * 2.4 * 1.5)), 3), por_fila=5)
    if objeto in COMIDA:
        sitios = "".join(
            f"\\draw[line width=1.2pt, fill=white] ({(i - (entre - 1) / 2) * 3.0:.2f},0) ellipse (1.3 and 0.75);"
            f"\\draw[line width=0.8pt] ({(i - (entre - 1) / 2) * 3.0:.2f},0) ellipse (0.95 and 0.5);"
            for i in range(entre))
    else:
        sitios = "".join(
            f"\\draw[line width=1.2pt, rounded corners=2mm, fill=white] ({(i - (entre - 1) / 2) * 3.0 - 1.3:.2f},-0.8) "
            f"rectangle ({(i - (entre - 1) / 2) * 3.0 + 1.3:.2f},0.8);"
            for i in range(entre))
    return (cosas + "\n\n\\vspace{10mm}\n"
            + f"\\begin{{tikzpicture}}{sitios}\\end{{tikzpicture}}")


def dibujo_ordena(pasos):
    """Cada paso, con su casilla para escribir el número. En cm."""
    filas = "\n".join(
        f"\\tikz[baseline=-1.5mm]\\draw[line width=1.1pt, rounded corners=1.5mm, fill=white] (0,-0.55) rectangle (1.1,0.55);"
        f" & {escapar(paso)} \\\\[5mm]" for paso in pasos)
    return ("{\\Large\\begin{tabularx}{\\linewidth}{@{}c@{\\hspace{5mm}}>{\\sinPartir\\arraybackslash}X@{}}\n"
            + filas + "\n\\end{tabularx}}")


def dibujo_hucha(semanas, L):
    """La hucha y, a su lado, una casilla por semana, con su número
    debajo, para ir apuntando lo que hay: en filas de 5, que caben en la
    caja con casillas grandes, para la letra de un niño. En cm. Debajo
    de cada casilla, qué semana es ("1.ª", "1st"): L.semana_hucha."""
    ancho, alto, hueco, por_fila = 1.75, 1.3, 0.2, 5
    piezas = [f"\\begin{{scope}}[shift={{(-1.75,-0.05)}}, scale=1.3, objeto]\\objHucha\\end{{scope}}"]
    for i in range(semanas):
        fila, col = divmod(i, por_fila)
        x, arriba = col * (ancho + hueco), 1.6 - fila * 2.0
        piezas.append(f"\\draw[line width=1.1pt, rounded corners=1mm, fill=white] ({x:.2f},{arriba - alto:.2f}) rectangle ({x + ancho:.2f},{arriba:.2f});"
                      f"\\node[font=\\footnotesize, text=colorGris] at ({x + ancho / 2:.2f},{arriba - alto - 0.3:.2f}) {{{L.semana_hucha(i + 1)}}};")
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_cuentas(empieza, apuntes, L):
    """El cuaderno de cuentas: una fila por apunte, con lo que entra o lo
    que sale, y una casilla para lo que queda. La primera fila, lo que
    hay al empezar, ya está escrita."""
    filas = [f"\\lblAlEmpezar & & & {L.euros_tabla(empieza)} \\\\ \\hline"]
    for texto, cantidad in apuntes:
        entra, sale = (L.euros_tabla(cantidad), "") if cantidad > 0 else ("", L.euros_tabla(-cantidad))
        filas.append(f"{escapar(texto)} & {entra} & {sale} & \\casillaCuenta[26mm] \\\\ \\hline")
    return ("{\\LARGE\\renewcommand{\\arraystretch}{2.2}"
            "\\begin{tabularx}{\\linewidth}{@{}>{\\sinPartir\\arraybackslash}X"
            ">{\\centering\\arraybackslash}p{24mm}>{\\centering\\arraybackslash}p{24mm}"
            ">{\\centering\\arraybackslash}p{30mm}@{}}\n"
            "\\textbf{\\lblQuePasa} & \\textbf{\\lblEntra} & \\textbf{\\lblSale} & \\textbf{\\lblQueda} \\\\ \\hline\n"
            + "\n".join(filas) + "\n\\end{tabularx}}")


def dibujo_tiendas(objeto, tiendas):
    """Dos tiendas, una al lado de la otra, con su nombre en el letrero y,
    en el escaparate, la misma cosa con su precio. En cm."""
    piezas = []
    for i, (nombre, precio) in enumerate(tiendas):
        x = (i - 0.5) * 6.6
        piezas.append(
            f"\\begin{{scope}}[shift={{({x:.2f},0)}}]\\tienda{{{escapar(nombre)}}}"
            f"\\begin{{scope}}[shift={{(0,-0.05)}}, scale=0.85, objeto]{OBJETOS[objeto]}\\end{{scope}}"
            f"\\begin{{scope}}[shift={{(0,-1.45)}}, scale=1.1, transform shape]{etiqueta(precio)}\\end{{scope}}"
            "\\end{scope}")
    return "\\begin{tikzpicture}[scale=1.2]\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


# --------------------------------------------------------------------
# Actividades
# --------------------------------------------------------------------
def render_actividad(d, L=ESPANOL):
    """(tex, clave): la caja de la actividad del día, y su entrada de la
    clave de respuestas (None si no tiene nada que comprobar), en la
    lengua L (tools/idiomas.py)."""
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
        defecto, instruccion, clave = L.clasifica(cajas, cosas)
        return PLANTILLA_CAJA.substitute(
            caja="cajaClasifica",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
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
        defecto, instruccion, clave = L.une(pares)
        return PLANTILLA_CAJA.substitute(
            caja="cajaUne",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_une([p[0] for p in pares], derecha),
        ), ("une", clave)

    if tipo == "vf":
        campos(num, a, ["frases"])
        frases = a["frases"]
        if not 3 <= len(frases) <= 5 or any(len(f) != 2 or not isinstance(f[1], bool) for f in frases):
            raise ErrorDeContenido(f"día {num}: 'vf' lleva de 3 a 5 frases, cada una [texto, true o false]")
        if len({f[1] for f in frases}) != 2:
            raise ErrorDeContenido(f"día {num}: en 'vf' hay alguna verdad y alguna mentira")
        defecto, instruccion, clave = L.vf(frases)
        return PLANTILLA_VF.substitute(
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            frases="\n".join(f"\\frasevf{{{i}}}{{{escapar(f[0])}}}" for i, f in enumerate(frases, 1)),
        ), ("vf", clave)

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
            raise ErrorDeContenido(f"día {num}: en 'trueque', {n} {L.cosa(de, n)} no se cambian justo")
        respuesta = n * notra // nde
        comprobar_cantidad(num, semana, respuesta, "en 'trueque', la respuesta")
        if n == nde:
            raise ErrorDeContenido(f"día {num}: en 'trueque', la pregunta no puede ser el mismo cambio de arriba")
        enunciado, instruccion, clave = L.trueque(oa, na, ob, nb, de, n, otra, respuesta)
        return PLANTILLA_CAJA.substitute(
            caja="cajaTrueque",
            enunciado=enunciado,
            instruccion=instruccion,
            dibujo=dibujo_trueque(oa, na, ob, nb, de, n, otra),
        ), ("trueque", clave)

    if tipo == "dinero":
        # Contar monedas y billetes.
        campos(num, a, ["dinero"])
        comprobar_dinero(num, semana, a["dinero"], "en 'dinero', las monedas y los billetes")
        if not 2 <= len(a["dinero"]) <= 8:
            raise ErrorDeContenido(f"día {num}: 'dinero' lleva de 2 a 8 monedas y billetes")
        defecto, instruccion, respuesta, clave = L.dinero(sum(a["dinero"]))
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaDinero",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_dinero(a["dinero"]),
            respuesta=respuesta,
        ), ("dinero", clave)

    if tipo == "reparte":
        # Repartir entre varios, y lo que sobra.
        campos(num, a, ["objeto", "total", "entre"])
        comprobar_objeto(num, a["objeto"])
        total, entre = a["total"], a["entre"]
        if not isinstance(total, int) or not 2 <= total <= 20 or not isinstance(entre, int) or not 2 <= entre <= 5:
            raise ErrorDeContenido(f"día {num}: 'reparte' reparte de 2 a 20 cosas, en 2 a 5 partes ({total}, {entre})")
        cada, sobran = divmod(total, entre)
        if cada < 1:
            raise ErrorDeContenido(f"día {num}: en 'reparte', a cada uno le toca al menos una")
        # "A cada uno", o lo que diga el JSON cuando se reparte entre
        # otras cosas: "En cada una" (estanterías), "Cada una" (mamás).
        cada_uno = a.get("cada", L.cada_uno)
        if not isinstance(cada_uno, str) or not cada_uno or len(cada_uno) > 14:
            raise ErrorDeContenido(f"día {num}: en 'reparte', 'cada' es un texto corto, como \"En cada una\" ({cada_uno!r})")
        defecto, instruccion, respuesta, clave = L.reparte(
            a["objeto"], total, entre, a["objeto"] in COMIDA, cada_uno, escapar(cada_uno), cada, sobran)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaReparte",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_reparte(a["objeto"], total, entre),
            respuesta=respuesta,
        ), ("reparte", clave)

    if tipo in ("compra", "llega"):
        # Cosas con su precio: sumar lo que se compra, o ver qué se puede
        # comprar con lo que se tiene.
        campos(num, a, ["cosas"] + (["compra"] if tipo == "compra" else ["tengo"]))
        cosas = a["cosas"]
        if not 2 <= len(cosas) <= 4 or len({c[0] for c in cosas}) != len(cosas):
            raise ErrorDeContenido(f"día {num}: '{tipo}' lleva de 2 a 4 cosas distintas, cada una con su precio")
        for objeto, precio in cosas:
            comprobar_objeto(num, objeto)
            if not isinstance(precio, int) or precio < 1:
                raise ErrorDeContenido(f"día {num}: en '{tipo}', cada cosa cuesta 1 € o más ({objeto}: {precio!r})")
            comprobar_cantidad(num, semana, precio, f"en '{tipo}', el precio de {L.un(objeto)}")
        precios = dict(cosas)
        if tipo == "compra":
            compra = a["compra"]
            if not compra or len(set(compra)) != len(compra) or any(c not in precios for c in compra):
                raise ErrorDeContenido(f"día {num}: en 'compra', lo que se compra es una o más de las cosas, sin repetir ({compra})")
            total = sum(precios[c] for c in compra)
            comprobar_cantidad(num, semana, total, "en 'compra', el total")
            defecto, instruccion, respuesta, clave = L.compra(compra, precios, total)
            return PLANTILLA_CON_RESPUESTA.substitute(
                caja="cajaCompra",
                enunciado=escapar(a.get("pregunta", defecto)),
                instruccion=instruccion,
                dibujo=dibujo_precios(cosas),
                respuesta=respuesta,
            ), ("compra", clave)
        tengo = a["tengo"]
        comprobar_cantidad(num, semana, tengo, "en 'llega', lo que se tiene")
        si = [o for o, pr in cosas if pr <= tengo]
        if not si or len(si) == len(cosas):
            raise ErrorDeContenido(f"día {num}: en 'llega', alguna cosa se puede comprar y alguna no")
        defecto, instruccion, clave = L.llega(tengo, si)
        return PLANTILLA_CAJA.substitute(
            caja="cajaLlega",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_precios(cosas),
        ), ("llega", clave)

    if tipo == "cambio":
        # La vuelta: se paga con más de lo que cuesta.
        campos(num, a, ["cosa", "paga"])
        objeto, precio = a["cosa"]
        comprobar_objeto(num, objeto)
        comprobar_cantidad(num, semana, precio, "en 'cambio', el precio")
        comprobar_dinero(num, semana, a["paga"], "en 'cambio', lo que se paga")
        pago = sum(a["paga"])
        if pago <= precio:
            raise ErrorDeContenido(f"día {num}: en 'cambio' se paga con más de lo que cuesta ({pago} €, {precio} €)")
        if any(pago - v >= precio for v in a["paga"]):
            raise ErrorDeContenido(f"día {num}: en 'cambio', sobra una de las monedas o billetes con que se paga ({a['paga']})")
        defecto, instruccion, respuesta, clave = L.cambio(objeto, precio, a["paga"], pago)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaVuelta",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=f"{dibujo_precios([(objeto, precio)])}\\hspace{{16mm}}{dibujo_dinero(a['paga'])}",
            respuesta=respuesta,
        ), ("vuelta", clave)

    if tipo == "problema":
        campos(num, a, ["texto", "operacion"])
        x, signo, y = a["operacion"]
        if signo not in SIGNOS:
            raise ErrorDeContenido(f"día {num}: en 'problema', la cuenta es una suma o una resta ({signo!r})")
        resultado = x + y if signo == "+" else x - y
        if resultado < 0:
            raise ErrorDeContenido(f"día {num}: en 'problema', la resta no baja del 0 ({x} − {y})")
        for v in (x, y, resultado):
            comprobar_cantidad(num, semana, v, "un número del problema")
        for v in (x, y):
            if not re.search(rf"(?<!\d){v}(?!\d)", a["texto"]):
                raise ErrorDeContenido(f"día {num}: el problema tiene que decir el {v}, con cifras: «{a['texto']}»")
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaProblema",
            enunciado=escapar(a["texto"]),
            instruccion=L.problema(),
            dibujo=r"\tikz\draw[dashed, line width=0.8pt, rounded corners=4mm, colorGris] (0,0) rectangle (13,5);",
            respuesta=f"\\huecoRespuesta\\ {SIGNOS[signo]} \\huecoRespuesta\\ = \\huecoRespuesta",
        ), ("problema", f"{x} {SIGNOS[signo]} {y} = {resultado}")

    if tipo == "botes":
        # Los tres botes: ahorrar, gastar y compartir; en uno falta lo que hay.
        campos(num, a, ["total", "botes", "falta", "pregunta"])
        total, botes, falta = a["total"], a["botes"], a["falta"]
        comprobar_cantidad(num, semana, total, "en 'botes', el dinero")
        if len(botes) != 3 or any(not isinstance(b, int) or b < 0 for b in botes) or sum(botes) != total:
            raise ErrorDeContenido(f"día {num}: en 'botes', los tres botes suman el dinero que hay ({botes}, {total})")
        if falta not in (0, 1, 2):
            raise ErrorDeContenido(f"día {num}: en 'botes', 'falta' es el bote que falta: 0, 1 o 2")
        for v in [total] + [b for i, b in enumerate(botes) if i != falta]:
            if not re.search(rf"(?<!\d){v}(?!\d)", a["pregunta"]):
                raise ErrorDeContenido(f"día {num}: la pregunta de 'botes' tiene que decir el {v}: «{a['pregunta']}»")
        nombres = [r"\lblAhorrar", r"\lblGastar", r"\lblCompartir"]
        contenidos = [r"\huecoRespuesta[22mm]" if i == falta else L.euros(b) for i, b in enumerate(botes)]
        tarros = r"\hspace{6mm}".join(f"\\bote{{{n}}}{{{c}}}" for n, c in zip(nombres, contenidos))
        instruccion, clave = L.botes(falta, botes[falta])
        return PLANTILLA_CAJA.substitute(
            caja="cajaBotes",
            enunciado=escapar(a["pregunta"]),
            instruccion=instruccion,
            dibujo=tarros,
        ), ("botes", clave)

    if tipo == "hucha":
        # Ahorrar tanto cada semana, hasta una meta.
        campos(num, a, ["tiene", "cada", "meta"])
        tiene, cada, meta = a["tiene"], a["cada"], a["meta"]
        for v, que in ((tiene, "lo que hay"), (cada, "lo que se ahorra cada semana"), (meta, "la meta")):
            comprobar_cantidad(num, semana, v, f"en 'hucha', {que}")
        if cada < 1 or meta <= tiene or (meta - tiene) % cada:
            raise ErrorDeContenido(f"día {num}: en 'hucha' se llega a la meta justo, ahorrando algo cada semana ({tiene}, {cada}, {meta})")
        semanas = (meta - tiene) // cada
        if semanas > 10:
            raise ErrorDeContenido(f"día {num}: en 'hucha' se llega a la meta en 10 semanas o menos ({semanas})")
        defecto, instruccion, respuesta, clave = L.hucha(tiene, cada, meta, semanas)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaHucha",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_hucha(10, L),
            respuesta=respuesta,
        ), ("hucha", clave)

    if tipo == "ordena":
        campos(num, a, ["pasos"])
        pasos = a["pasos"]
        if not 3 <= len(pasos) <= 5 or len(set(pasos)) != len(pasos):
            raise ErrorDeContenido(f"día {num}: 'ordena' lleva de 3 a 5 pasos, distintos")
        rng, orden = random.Random(num), list(pasos)
        while orden == pasos:
            rng.shuffle(orden)
        defecto, instruccion, clave = L.ordena([pasos.index(x) + 1 for x in orden])
        return PLANTILLA_CAJA.substitute(
            caja="cajaOrdena",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_ordena(orden),
        ), ("ordena", clave)

    if tipo == "elige":
        # Solo llega para una: la que se elige, y la que se deja.
        campos(num, a, ["tengo", "cosas"])
        tengo, cosas = a["tengo"], a["cosas"]
        comprobar_cantidad(num, semana, tengo, "en 'elige', lo que se tiene")
        if not 2 <= len(cosas) <= 3 or len({c[0] for c in cosas}) != len(cosas):
            raise ErrorDeContenido(f"día {num}: 'elige' lleva 2 o 3 cosas distintas, cada una con su precio")
        for objeto, precio in cosas:
            comprobar_objeto(num, objeto)
            if not isinstance(precio, int) or not 1 <= precio <= tengo:
                raise ErrorDeContenido(f"día {num}: en 'elige', cada cosa se puede comprar con lo que se tiene "
                                       f"({objeto}: {precio!r}, y hay {tengo} €)")
        if any(p + q <= tengo for (_, p), (_, q) in itertools.combinations(cosas, 2)):
            raise ErrorDeContenido(f"día {num}: en 'elige' no llega para dos cosas; si llegara, no habría "
                                   f"que elegir ({cosas}, {tengo} €)")
        defecto, instruccion, respuesta, clave = L.elige(tengo, cosas)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaElige",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_precios(cosas),
            respuesta=respuesta,
        ), ("elige", clave)

    if tipo == "compara":
        # La misma cosa en dos tiendas: dónde es más barata, y cuánto se ahorra.
        campos(num, a, ["objeto", "tiendas", "pregunta"])
        comprobar_objeto(num, a["objeto"])
        tiendas = a["tiendas"]
        if len(tiendas) != 2 or any(len(t) != 2 for t in tiendas):
            raise ErrorDeContenido(f"día {num}: 'compara' lleva dos tiendas, cada una [nombre, precio]")
        (n1, p1), (n2, p2) = tiendas
        if not all(isinstance(n, str) and 0 < len(n) <= 14 for n in (n1, n2)) or n1 == n2:
            raise ErrorDeContenido(f"día {num}: en 'compara', cada tienda tiene su nombre, corto y distinto ({n1!r}, {n2!r})")
        for pr in (p1, p2):
            if not isinstance(pr, int) or pr < 1:
                raise ErrorDeContenido(f"día {num}: en 'compara', cada precio es de 1 € o más ({pr!r})")
            comprobar_cantidad(num, semana, pr, "en 'compara', un precio")
            if not re.search(rf"(?<!\d){pr}(?!\d)", a["pregunta"]):
                raise ErrorDeContenido(f"día {num}: la pregunta de 'compara' tiene que decir el {pr}: «{a['pregunta']}»")
        if p1 == p2:
            raise ErrorDeContenido(f"día {num}: en 'compara', los precios son distintos; si no, no hay nada que comparar")
        instruccion, respuesta, clave = L.compara(*sorted(tiendas, key=lambda t: t[1]))
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaCompara",
            enunciado=escapar(a["pregunta"]),
            instruccion=instruccion,
            dibujo=dibujo_tiendas(a["objeto"], tiendas),
            respuesta=respuesta,
        ), ("compara", clave)

    if tipo == "cuentas":
        # El cuaderno de cuentas: lo que entra, lo que sale y lo que queda.
        campos(num, a, ["empieza", "apuntes"])
        empieza, apuntes = a["empieza"], a["apuntes"]
        comprobar_cantidad(num, semana, empieza, "en 'cuentas', lo que hay al empezar")
        if not 3 <= len(apuntes) <= 5:
            raise ErrorDeContenido(f"día {num}: 'cuentas' lleva de 3 a 5 apuntes")
        queda, quedas = empieza, []
        for apunte in apuntes:
            if (len(apunte) != 2 or not isinstance(apunte[0], str) or not 0 < len(apunte[0]) <= 30
                    or not isinstance(apunte[1], int) or apunte[1] == 0):
                raise ErrorDeContenido(f"día {num}: cada apunte de 'cuentas' es [texto corto, cantidad], "
                                       f"con la cantidad en positivo si entra y en negativo si sale ({apunte})")
            comprobar_cantidad(num, semana, abs(apunte[1]), "en 'cuentas', un apunte")
            queda += apunte[1]
            if queda < 0:
                raise ErrorDeContenido(f"día {num}: en 'cuentas' nunca queda menos de 0 "
                                       f"(después de «{apunte[0]}» quedarían {queda} €)")
            comprobar_cantidad(num, semana, queda, "en 'cuentas', lo que queda")
            quedas.append(queda)
        if not any(x[1] > 0 for x in apuntes) or not any(x[1] < 0 for x in apuntes):
            raise ErrorDeContenido(f"día {num}: en 'cuentas', algo entra y algo sale")
        defecto, instruccion, clave = L.cuentas(quedas)
        return PLANTILLA_CAJA.substitute(
            caja="cajaCuentas",
            enunciado=escapar(a.get("pregunta", defecto)),
            instruccion=instruccion,
            dibujo=dibujo_cuentas(empieza, apuntes, L),
        ), ("cuentas", clave)

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


# Lo que se escribe a mano en cada actividad: lo que cada traducción
# trae en su lengua ("First Economics" en content/english/q*.json,
# "Poznaję ekonomię" en content/polish/q*.json). Todo lo demás -- las
# cosas, los precios, el dinero, en qué caja va cada tarjeta, qué frase
# es verdad -- es lo de "Aprendo economía", y el enunciado que no se
# escribe a mano lo compone tools/idiomas.py. Un texto que un día en
# español puede traer o no ('pregunta', 'cada') lo trae el día en otra
# lengua si, y solo si, lo trae el día en español.
TEXTOS_ACTIVIDAD = {
    "clasifica": ("pregunta", "cajas", "cosas"),
    "une": ("pregunta", "pares"),
    "vf": ("pregunta", "frases"),
    "trueque": (),
    "dinero": ("pregunta",),
    "reparte": ("pregunta", "cada"),
    "compra": ("pregunta",),
    "llega": ("pregunta",),
    "cambio": ("pregunta",),
    "problema": ("texto",),
    "botes": ("pregunta",),
    "hucha": ("pregunta",),
    "ordena": ("pregunta", "pasos"),
    "elige": ("pregunta",),
    "compara": ("pregunta", "tiendas"),
    "cuentas": ("pregunta", "apuntes"),
    "dibuja": ("prompt",),
    "repasa": ("checklist", "prompt"),
}


def _forma(valor):
    """Lo que no se traduce de un valor del JSON: el mismo valor, con
    cada texto cambiado por str. Las tarjetas de "Clasifica" en otra
    lengua son las mismas, en el mismo orden y en las mismas cajas; las frases
    de "¿Verdad o mentira?", las mismas verdades y las mismas mentiras;
    las tiendas de "Compara", los mismos precios; los apuntes de "Las
    cuentas", las mismas cantidades. Así todos los cuadernos son, página
    a página, el mismo: también cuando se barajan (random.Random(día))."""
    if isinstance(valor, str):
        return str
    if isinstance(valor, list):
        return [_forma(v) for v in valor]
    return type(valor), valor


def _textos(valor):
    """Todos los textos de un valor del JSON."""
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, list):
        for v in valor:
            yield from _textos(v)
    elif isinstance(valor, dict):
        for v in valor.values():
            yield from _textos(v)


def comprobar_euros(L, donde, valor):
    """Cada lengua escribe el dinero a su manera: en inglés, €5; en
    polaco, 5 €, como en español (L.euro_mal, en tools/idiomas.py)."""
    for texto in _textos(valor):
        if L.euro_mal and L.euro_mal.search(texto):
            raise ErrorDeContenido(f"{donde}: {L.aviso_euro} («{texto}»)")


def cargar_traduccion(dias_es, cuaderno):
    """Los días de una traducción ("First Economics", "Poznaję
    ekonomię"): los de "Aprendo economía", uno a uno, con el tema de su
    semana en su lengua (tools/idiomas.py), y su historia y los textos de
    su actividad de content/<lengua>/q*.json (TEXTOS_ACTIVIDAD); y las
    palabras de las semanas, en su lengua, de las 'semanas' de esos mismos
    ficheros. La actividad es la misma, con las mismas cosas, los mismos
    números y las mismas respuestas: de cada texto, solo cambia la
    lengua."""
    L, carpeta = cuaderno.lengua, cuaderno.carpeta.relative_to(ROOT)
    textos, semanas = {}, {}
    for ruta in sorted(cuaderno.carpeta.glob("q*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        for t in datos["dias"]:
            if t.get("dia") in textos:
                raise ErrorDeContenido(f"el día {t.get('dia')} está dos veces en {carpeta}/")
            textos[t.get("dia")] = t
        for s in datos.get("semanas", []):
            if s.get("semana") in semanas:
                raise ErrorDeContenido(f"la semana {s.get('semana')} está dos veces en las 'semanas' de {carpeta}/")
            semanas[s.get("semana")] = s
    total = cuaderno.escritos or TOTAL_DIAS
    if total > len(dias_es):
        raise ErrorDeContenido("no puede tener días que no tenga todavía «Aprendo economía»")
    if sorted(textos) != list(range(1, total + 1)):
        raise ErrorDeContenido(
            f"tienen que estar los días del 1 al {total} en {carpeta}/, sin huecos ni repetidos"
            + (f" (en obras: {cuaderno.constante})" if cuaderno.escritos else ""))
    for n, s in semanas.items():
        comprobar_euros(L, f"semana {n}", s)
    dias = []
    for d in dias_es[:total]:
        num, t = d["dia"], textos[d["dia"]]
        sobran = set(t) - {"dia", "historia", "actividad"}
        if sobran:
            raise ErrorDeContenido(f"día {num}: no se usa {', '.join(sorted(sobran))}")
        if not isinstance(t.get("historia"), str) or not t["historia"]:
            raise ErrorDeContenido(f"día {num}: falta 'historia'")
        es, en = d["actividad"], t.get("actividad")
        tipo = es["tipo"]
        if not isinstance(en, dict) or en.get("tipo") != tipo:
            raise ErrorDeContenido(
                f"día {num}: la actividad es la de «Aprendo economía», con su tipo: "
                f"{{\"tipo\": \"{tipo}\"}} ({en!r})")
        traducibles = TEXTOS_ACTIVIDAD[tipo]
        sobran = set(en) - {"tipo"} - set(traducibles)
        if sobran:
            raise ErrorDeContenido(
                f"día {num}: de '{tipo}' se traduce " + (", ".join(f"'{c}'" for c in traducibles) or "nada")
                + f", y {', '.join(sorted(sobran))} es lo de «Aprendo economía»")
        a = dict(es)
        for c in traducibles:
            if (c in en) != (c in es):
                raise ErrorDeContenido(
                    f"día {num}: '{tipo}' " + ("lleva" if c in es else "no lleva")
                    + f" '{c}', como el día en «Aprendo economía»")
            if c in en:
                if _forma(en[c]) != _forma(es[c]):
                    raise ErrorDeContenido(
                        f"día {num}: en '{tipo}', '{c}' es lo mismo que en «Aprendo economía», en {L.nombre_lengua}: "
                        f"los mismos textos, en el mismo orden y con los mismos números ({en[c]!r})")
                a[c] = en[c]
        comprobar_euros(L, f"día {num}", [t["historia"]] + [en[c] for c in traducibles if c in en])
        dias.append(dict(d, tema=L.temas[d["semana"] - 1], historia=t["historia"], actividad=a))
    return dias, semanas


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


def validar_dias(dias, semanas, L=ESPANOL, escritos=DIAS_ESCRITOS):
    total = escritos or TOTAL_DIAS
    numeros = [d["dia"] for d in dias]
    if numeros != list(range(1, total + 1)):
        raise ErrorDeContenido(
            f"tienen que estar los días del 1 al {total}, sin huecos ni repetidos"
            + (" (en obras: DIAS_ESCRITOS)" if escritos else "")
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
        if d.get("tema") != L.temas[semana - 1]:
            raise ErrorDeContenido(
                f"día {num}: el tema de la semana {semana} es «{L.temas[semana - 1]}», "
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
    "% GENERADO por tools/gen_economia.py a partir de {fuentes}.\n"
    "% NO EDITAR A MANO -- los cambios se perderán en la siguiente\n"
    "% ejecución de `make generate`. Edita {fuentes} en su lugar.\n\n"
)


def generar(dias, semanas, cuaderno, fuentes):
    L = cuaderno.lengua
    piezas = [CABECERA.format(nombre=cuaderno.salida_dias.relative_to(ROOT), fuentes=fuentes)]
    claves = [CABECERA.format(nombre=cuaderno.salida_clave.relative_to(ROOT), fuentes=fuentes)]
    for d in dias:
        num, semana = d["dia"], d["semana"]
        trimestre = trimestre_de(semana)
        palabra = semanas[semana]
        d = dict(d, palabra_semana=palabra)
        actividad, clave = render_actividad(d, L)
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
        if num == ULTIMO_DIA_TRIMESTRE.get(trimestre) and trimestre in L.nombre_medalla:
            piezas.append(L.plantilla_medalla.substitute(dia=num, estacion=L.nombre_medalla[trimestre]))
    # "Mi diccionario de economía": las palabras de las semanas, por orden
    # alfabético (en español, sin tildes para ordenar: "ahorro" antes que
    # "árbol").
    orden = sorted(semanas.values(), key=lambda s: L.orden_alfabetico(s["palabra"]))
    diccionario = CABECERA.format(nombre=cuaderno.salida_diccionario.relative_to(ROOT), fuentes=fuentes) + "".join(
        f"\\entradaDiccionario{{{escapar(s['palabra'].capitalize())}}}{{{escapar(s['definicion'])}}}{{{s['semana']}}}\n"
        for s in orden)
    return "\n".join(piezas), "".join(claves), diccionario


def comprobar_totaldias(cuaderno):
    """lang/es.tex y lang/en.tex prometen los mismos 260 días que este
    script."""
    m = re.search(r"\\newcommand\{\\totaldias\}\{(\d+)\}", cuaderno.lang.read_text(encoding="utf-8"))
    if not m or int(m.group(1)) != TOTAL_DIAS:
        raise ErrorDeContenido(f"\\totaldias en {cuaderno.lang.relative_to(ROOT)} tiene que ser {TOTAL_DIAS}")


def main():
    check_only = "--check" in sys.argv
    salidas, resumen = [], []
    for cuaderno in (APRENDO,) + TRADUCCIONES:
        escritos = cuaderno.escritos
        try:
            comprobar_totaldias(cuaderno)
            if cuaderno is APRENDO:
                dias, semanas = cargar()
                dias_es = dias
                fuentes = "content/q*.json"
            else:
                dias, semanas = cargar_traduccion(dias_es, cuaderno)
                fuentes = f"content/q*.json y {cuaderno.carpeta.relative_to(ROOT)}/q*.json"
            validar_dias(dias, semanas, cuaderno.lengua, escritos)
            tex, clave, diccionario = generar(dias, semanas, cuaderno, fuentes)
        except ErrorDeContenido as exc:
            print(f"ERROR ({cuaderno.nombre}): {exc}", file=sys.stderr)
            return 1
        salidas += [(cuaderno.salida_dias, tex), (cuaderno.salida_clave, clave),
                    (cuaderno.salida_diccionario, diccionario)]
        obras = f", en obras: {len(dias)} de {TOTAL_DIAS} días escritos" if escritos else ""
        resumen.append(f"{cuaderno.nombre} ({len(dias)} días{obras})")

    if check_only:
        for ruta, contenido in salidas:
            actual = ruta.read_text(encoding="utf-8") if ruta.exists() else None
            if actual != contenido:
                print(
                    f"DESACTUALIZADO: {ruta.relative_to(ROOT)} no coincide con su JSON "
                    "-- ejecuta `make generate`.",
                    file=sys.stderr,
                )
                return 1
        print(f"OK: {' y '.join(resumen)} validados, y lo generado, al día.")
        return 0

    for ruta, contenido in salidas:
        ruta.write_text(contenido, encoding="utf-8")
    print(f"Escritos: {' y '.join(resumen)}, con su clave y su diccionario.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
