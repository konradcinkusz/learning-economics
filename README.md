# Aprendo economía

[![Build](https://github.com/konradcinkusz/learning-economics/actions/workflows/build.yml/badge.svg)](https://github.com/konradcinkusz/learning-economics/actions/workflows/build.yml)
[![Licencia](https://img.shields.io/github/license/konradcinkusz/learning-economics)](LICENSE)
[![Hecho con](https://img.shields.io/badge/hecho%20con-LaTeX-2E7D32)](preamble.tex)

Un cuaderno diario de economía en español, A4, una página por día
laborable del año: para una niña o un niño de siete u ocho años (2.º de
Primaria) que ya lee sola y ya suma y resta hasta 20. No enseña cuentas
de mayores, sino las ideas de la economía de cada día: que las cosas
tienen valor, que el dinero sirve para cambiar unas cosas por otras, que
no se puede tener todo y hay que elegir, que ahorrar es guardar hoy para
mañana, que alguien hace el pan que compramos, que las aceras y los
parques los pagamos entre todos. Y las cuentas que hacen falta para eso:
contar dinero, sumar precios, calcular la vuelta, repartir, ahorrar un
poco cada semana.

Es de la misma familia que
[**Aprendo a leer**](https://github.com/konradcinkusz/learning-to-read) y
[**Aprendo los números**](https://github.com/konradcinkusz/learning-to-count):
el mismo motor, la misma familia (Lucía, su hermano Dani, su perro Toby,
Mamá, Papá y la abuela Rosa), y los temas de *Leo con lupa*, el tercer
cuaderno de *Aprendo a leer*, semana a semana: el Club de la Lupa (Lucía,
Sofía y Hugo), la lupa del padre de la abuela, que era relojero, y en
verano, el pueblo. Quien lleve los dos cuadernos se encuentra la misma
semana en los dos: en uno se investiga el caso, y en el otro se piensa
en lo que cuesta, en lo que vale y en quién lo hace.

Cada página tiene, arriba, **Hoy**: la historia del día, dos o tres
frases que lee la niña o el niño, y un dibujo; los lunes, además, **la
palabra de la semana** (*valor*, *trueque*, *dinero*, *escasez*,
*ahorro*, *precio*...) y lo que quiere decir -- al final del cuaderno
están todas, en *Mi diccionario de economía*. Debajo, una
**actividad**: clasificar, unir, decir si es verdad o mentira, cambiar
cosas (el trueque), dibujar, y los viernes, repasar; y con el año,
contar dinero, repartir, sumar lo que cuesta la compra, calcular la
vuelta, ahorrar para una meta, elegir, comparar precios y llevar las
cuentas.

El dinero crece con el año, como los números en *Aprendo los números*:
hasta 20 € en otoño, hasta 50 € en invierno y hasta 100 € en primavera
y en verano, siempre en euros enteros.

El plan completo, semana a semana, está en
[`notes/01-plan.md`](notes/01-plan.md).

## First Economics (en inglés)

El mismo cuaderno en inglés (británico, como *First Numbers*, el
*Aprendo los números* en inglés, y como *Read and Draw* y *First Words*
de *Aprendo a leer*), **página a página**: la misma historia, el mismo
dibujo y la misma actividad cada día, con las mismas cosas, los mismos
precios y las mismas respuestas, así que se puede hacer uno, el otro o
los dos. Lo que cambia es la lengua: la historia, los temas, las
palabras de la semana (*value*, *barter*, *money*, *scarcity*...), los
enunciados, las instrucciones, las páginas para el adulto, la clave, *My
economics dictionary* y el diploma. Los personajes y lo que es de aquí
se quedan como en esos cuadernos (Lucía, Grandma Rosa, el roscón, los
churros), y el dinero son euros, escritos a la inglesa: €5.

Está en `english.tex` (y `english-bw.tex`), con el texto de cada día en
`content/english/q*.json`; todo lo que se escribe en una lengua o en la
otra sale de `tools/idiomas.py`, y las comprobaciones son las mismas. El
plan, en [`notes/02-english.md`](notes/02-english.md).

## Poznaję ekonomię (en polaco)

El mismo cuaderno en polaco, **página a página**, como *First
Economics*: la misma historia, el mismo dibujo y la misma actividad
cada día, con las mismas cosas, los mismos precios y las mismas
respuestas. Lo que cambia es la lengua: la historia, los temas, las
palabras de la semana (*wartość*, *handel wymienny*, *pieniądze*,
*niedobór*...), los enunciados, con cada número y su palabra en la
forma que le toca (*1 muszelka*, *2 karty*, *5 kart*), las
instrucciones, las páginas para el adulto, la clave, *Mój słowniczek
ekonomiczny* y el diploma. Los personajes se quedan (Lucía, babcia
Rosa, pan Paco, pani Marta), y el dinero son euros, escritos como en
español: 5 €.

Está en `polish.tex` (y `polish-bw.tex`), con el texto de cada día en
`content/polish/q*.json`, y las comprobaciones son las mismas. El plan,
en [`notes/03-polish.md`](notes/03-polish.md).

## Descargar el PDF sin instalar nada

**[⬇ PDF (color)](https://konradcinkusz.github.io/learning-economics/aprendo-economia.pdf)**
· **[⬇ PDF (blanco y negro)](https://konradcinkusz.github.io/learning-economics/aprendo-economia-bn.pdf)**

*First Economics*: **[⬇ PDF (colour)](https://konradcinkusz.github.io/learning-economics/first-economics.pdf)**
· **[⬇ PDF (black and white)](https://konradcinkusz.github.io/learning-economics/first-economics-bw.pdf)**

*Poznaję ekonomię*: **[⬇ PDF (kolorowy)](https://konradcinkusz.github.io/learning-economics/poznaje-ekonomie.pdf)**
· **[⬇ PDF (czarno-biały)](https://konradcinkusz.github.io/learning-economics/poznaje-ekonomie-cz-b.pdf)**

Enlaces fijos, publicados por GitHub Pages en cada push a `main` (ver
`.github/workflows/pages.yml`). Las dos versiones tienen exactamente el
mismo contenido y la misma paginación: nada en el cuaderno se distingue
solo por el color. Mientras Pages no esté activado, los mismos PDF están
en la pestaña *Actions* → el último run de *Build* → artefactos
`pdf-color` / `pdf-bw` -- y los de *First Economics*, `pdf-english` /
`pdf-english-bw`; y los de *Poznaję ekonomię*, `pdf-polish` /
`pdf-polish-bw`.

## Construir el PDF a mano

Necesita una distribución de TeX con **LuaLaTeX** (la letra es Andika,
cargada con `fontspec` desde `fonts/andika/`) + `latexmk`, con `babel`,
`tcolorbox` y `tikz`, y Python 3.

```sh
make              # genera, compila el cuaderno en color y comprueba
make english      # lo mismo, "First Economics" (english.tex)
make polish       # lo mismo, "Poznaję ekonomię" (polish.tex)
make all-formats  # los seis PDF, color Y blanco-y-negro de los tres -- lo que corre el CI
make generate     # solo regenera los .tex de los tres cuadernos desde el JSON
make build        # solo compila en color (asume que ya está generado)
make build-bw     # solo compila en blanco y negro
make check        # lee main.log + 1 día = 1 página (main.aux) + valida el JSON
make clean
```

## Estructura

```
main.tex, main-bw.tex          -- el cuaderno, color y blanco-y-negro; solo fijan \bookcolor
english.tex, english-bw.tex    -- "First Economics": lo mismo, con \booklang{english}
polish.tex, polish-bw.tex      -- "Poznaję ekonomię": lo mismo, con \booklang{polish}
preamble.tex, lang/es.tex      -- el motor LaTeX y todas las cadenas de texto
lang/en.tex, lang/pl.tex       -- las mismas cadenas, en inglés y en polaco
body.tex, body-english.tex, body-polish.tex -- el orden del documento
frontmatter/, backmatter/      -- portada, instrucciones, mapa del curso; clave, diccionario y diploma
frontmatter/english/, backmatter/english/ -- lo mismo, en inglés (y frontmatter/polish/, backmatter/polish/, en polaco)
content/q1.json ...            -- las semanas (su palabra) y los días, uno por trimestre, editados a mano
content/english/q1.json ...    -- el texto en inglés de cada día y las palabras de la semana (lo demás es el de content/q*.json)
content/polish/q1.json ...     -- lo mismo, en polaco
content/generated-*.tex        -- GENERADO por tools/gen_economia.py, no editar (y content/english/, content/polish/generated-*.tex)
diagrams/kit.tex               -- las piezas de los dibujos de «First Words» (de Aprendo a leer)
diagrams/objetos.tex           -- las cosas de Aprendo los números, con las monedas y los billetes
diagrams/economia.tex          -- las cosas nuevas de este cuaderno: la lupa, los cromos, la hucha...
tools/gen_economia.py          -- JSON -> LaTeX, la escalera del dinero, las comprobaciones, la clave y el diccionario
tools/idiomas.py               -- lo que se escribe en la página, en español, en inglés y en polaco
tools/checklog.py              -- lee el .log de LuaLaTeX correctamente (de Aprendo a leer)
tools/check_pages.py           -- comprueba que cada día ocupa una sola página (de Aprendo a leer)
docs/index.html                -- la página que publica .github/workflows/pages.yml
notes/01-plan.md               -- el plan: las 52 semanas, las actividades, las comprobaciones y las fases
notes/02-english.md            -- el plan de "First Economics"
notes/03-polish.md             -- el plan de "Poznaję ekonomię"
```

## Licencia

Como *Aprendo a leer*: el motor -- LaTeX, los dibujos, las herramientas,
el `Makefile` y el CI -- está bajo MIT ([`LICENSE-CODE`](LICENSE-CODE));
el contenido -- los días de `content/q*.json`, la historia y lo que se
genera de ahí -- bajo Creative Commons BY-NC-SA 4.0
([`LICENSE-CONTENT`](LICENSE-CONTENT)); la letra Andika, bajo la SIL Open
Font License 1.1 ([`fonts/andika/OFL.txt`](fonts/andika/OFL.txt)). Ver
[`LICENSE`](LICENSE).

## Estado

**Completo.** Los 260 días, las 52 semanas de *Leo con lupa* con sus 52
palabras: el valor de las cosas, el trueque y el dinero, lo que es de
todos, el ahorro y el precio (otoño); elegir, comparar precios,
producir, cuidar, el presupuesto, el coste y los servicios (invierno);
el euro, el gasto, el sueldo, las tiendas, la cadena de la miel, el
banco y vender, con el cuaderno de cuentas (primavera); y la prioridad,
la medida, la demanda, el deseo, el oficio, la paga, el tesoro, la
ganancia, las rebajas y planear, hasta la palabra que lo junta todo:
*economía* (verano). Con sus tres medallas, la clave de respuestas, *Mi
diccionario de economía* y el diploma, en color y en blanco y negro.
Cada push comprueba el cuaderno entero: 1 día = 1 página, ninguna caja
que se salga, y todas las cuentas y la clave, calculadas por el script.
Se escribió en cinco fases, como *Aprendo los números*: ver "Las fases"
en [`notes/01-plan.md`](notes/01-plan.md).

**First Economics**, también completo: los 260 días en inglés, con sus
52 palabras (de *value* a *economics*), sus medallas, sus respuestas, *My
economics dictionary* y su diploma, en color y en blanco y negro,
publicado junto al español. Se escribió en tres fases: ver
[`notes/02-english.md`](notes/02-english.md).

**Poznaję ekonomię**, también completo: los 260 días en polaco, con sus
52 palabras (de *wartość* a *ekonomia*), sus medallas, sus respuestas,
*Mój słowniczek ekonomiczny* y su diploma, en color y en blanco y negro,
publicado junto a los otros dos. Se escribió en tres fases: ver
[`notes/03-polish.md`](notes/03-polish.md).
