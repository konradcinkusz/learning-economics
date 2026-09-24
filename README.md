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

## Descargar el PDF sin instalar nada

**[⬇ PDF (color)](https://konradcinkusz.github.io/learning-economics/aprendo-economia.pdf)**
· **[⬇ PDF (blanco y negro)](https://konradcinkusz.github.io/learning-economics/aprendo-economia-bn.pdf)**

Enlaces fijos, publicados por GitHub Pages en cada push a `main` (ver
`.github/workflows/pages.yml`). Las dos versiones tienen exactamente el
mismo contenido y la misma paginación: nada en el cuaderno se distingue
solo por el color. Mientras Pages no esté activado, los mismos PDF están
en la pestaña *Actions* → el último run de *Build* → artefactos
`pdf-color` / `pdf-bw`.

## Construir el PDF a mano

Necesita una distribución de TeX con **LuaLaTeX** (la letra es Andika,
cargada con `fontspec` desde `fonts/andika/`) + `latexmk`, con `babel`,
`tcolorbox` y `tikz`, y Python 3.

```sh
make              # genera, compila el cuaderno en color y comprueba
make all-formats  # los dos PDF, color Y blanco-y-negro -- lo que corre el CI
make generate     # solo regenera los .tex desde el JSON
make build        # solo compila en color (asume que ya está generado)
make build-bw     # solo compila en blanco y negro
make check        # lee main.log + 1 día = 1 página (main.aux) + valida el JSON
make clean
```

## Estructura

```
main.tex, main-bw.tex          -- el cuaderno, color y blanco-y-negro; solo fijan \bookcolor
preamble.tex, lang/es.tex      -- el motor LaTeX y todas las cadenas de texto
body.tex                       -- el orden del documento
frontmatter/, backmatter/      -- portada, instrucciones, mapa del curso; clave, diccionario y diploma
content/q1.json ...            -- las semanas (su palabra) y los días, uno por trimestre, editados a mano
content/generated-*.tex        -- GENERADO por tools/gen_economia.py, no editar
diagrams/kit.tex               -- las piezas de los dibujos de «First Words» (de Aprendo a leer)
diagrams/objetos.tex           -- las cosas de Aprendo los números, con las monedas y los billetes
diagrams/economia.tex          -- las cosas nuevas de este cuaderno: la lupa, los cromos, la hucha...
tools/gen_economia.py          -- JSON -> LaTeX, la escalera del dinero, las comprobaciones, la clave y el diccionario
tools/checklog.py              -- lee el .log de LuaLaTeX correctamente (de Aprendo a leer)
tools/check_pages.py           -- comprueba que cada día ocupa una sola página (de Aprendo a leer)
docs/index.html                -- la página que publica .github/workflows/pages.yml
notes/01-plan.md               -- el plan: las 52 semanas, las actividades, las comprobaciones y las fases
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

**En obras**: el motor, el diseño, el otoño y el invierno (días
1--130: el valor de las cosas, el trueque y el dinero, lo que es de
todos, el ahorro y el precio; elegir, comparar precios, producir,
cuidar, el presupuesto, el coste y los servicios), con sus dos
medallas. Se escribe
en cinco fases, un PR cada una, como *Aprendo los números*: ver "Las
fases" en [`notes/01-plan.md`](notes/01-plan.md).
