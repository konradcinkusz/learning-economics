# Cómo contribuir

Este repositorio es un cuaderno para niñas y niños de siete u ocho años,
generado desde JSON. Antes de tocar el contenido, lee
[`README.md`](README.md) y [`notes/01-plan.md`](notes/01-plan.md).

## Preparar el entorno (sin LaTeX)

Las comprobaciones y las pruebas solo necesitan Python 3:

```sh
python3 -m pip install -r requirements.txt   # solo pytest
make generate    # JSON -> content/**/generated-*.tex (no están en git)
make test        # pytest de tools/ (fixtures sintéticas)
make links       # los enlaces a PDF de docs/ y README existen en pages.yml
python3 tools/gen_economia.py --check
```

Compilar los PDF necesita LuaLaTeX y `latexmk`; el CI lo hace en cada push.
Si no tienes LaTeX, el CI es quien comprueba "1 día = 1 página".

## Añadir o cambiar un día

La fuente de verdad es el JSON; los `generated-*.tex` no se editan.

1. El calendario es fijo: 260 días, 52 semanas de 5 días, 13 semanas por
   trimestre. El día `N` es de la semana `(N-1)//5 + 1`, y su `tema` es el
   de esa semana en `tools/idiomas.py`. Cambiar el número de días o de
   semanas es cambiar el motor (`TOTAL_DIAS` en `tools/gen_economia.py`,
   `SALTOS_ESPERADOS` en `tools/check_pages.py`, `\totaldias` en
   `lang/*.tex`): abre antes una incidencia.
2. Escribe el día en `content/q<trimestre>.json`: `dia`, `semana`, `tema`,
   `objeto` (un dibujo que exista), `historia` (hasta 60 palabras) y
   `actividad`. Los lunes la historia dice la palabra de la semana; los
   viernes la actividad es `repasa`, y solo los viernes.
3. El dinero sigue la escalera del trimestre (`MAX_EUROS`, `BILLETES`) y
   cada tipo de actividad llega en su semana (`DESDE_SEMANA`).
4. Escribe el mismo día en `content/english/q*.json` y en
   `content/polish/q*.json` (ver "Paridad").
5. Ejecuta `make generate`, `make test` y `python3 tools/gen_economia.py --check`.
   `python3 tools/vocab_report.py --context` avisa (sin fallar) de las
   palabras de la semana que se usan antes de su semana.

## Paridad: tres lenguas, el mismo cuaderno

"Aprendo economía", "First Economics" y "Poznaję ekonomię" son el mismo
cuaderno, **página a página**: el mismo día tiene la misma historia, el
mismo dibujo, las mismas cosas, los mismos precios y las mismas
respuestas. Una traducción solo trae lo que cambia con la lengua: la
`historia`, los textos de la actividad (`TEXTOS_ACTIVIDAD`) y las
`semanas` (palabra, definición y formas). Todo lo demás sale del español, y
`cargar_traduccion` rechaza una traducción que cambie el tipo de
actividad, los números o el orden de los textos. Un día que falta en inglés o en polaco, o una actividad que no
coincide con la española, no pasa `--check`; que el texto diga lo mismo
lo revisa una persona.

## Personajes sintéticos

Todos los personajes son inventados (la familia de Lucía, el Club de la
Lupa, y los vecinos y tenderos del barrio). No uses nombres, fotos,
historias ni datos de niñas, niños o familias reales, ni documentos de
clientes o de colegios, ni en el contenido ni en los tests: las fixtures
son siempre sintéticas. Tampoco secretos ni claves en ningún fichero.

## Reglas de las comprobaciones

- No se debilita ni se quita una comprobación para que pase el CI: se
  arregla lo que falla. Ninguna lleva `continue-on-error`.
- Un cambio en `tools/` lleva su prueba en `tests/`, con un caso que
  falla.
- Código y comentarios: como el resto del repositorio. Los PDF y los
  `generated-*` no se suben.
