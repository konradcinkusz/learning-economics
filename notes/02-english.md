# «First Economics» — el cuaderno en inglés

*Aprendo economía* en inglés, **página a página**: la misma historia,
el mismo dibujo y la misma actividad cada día -- con las mismas cosas,
los mismos precios, el mismo dinero y las mismas respuestas --, así que
una niña o un niño puede hacer uno, el otro o los dos. Es para quien
aprende inglés en el colegio, como Lucía en *Read and Draw* y *First
Words* (de *Aprendo a leer*), y también para una familia que hable
inglés en casa; y es de la misma familia que *First Numbers*, el
*Aprendo los números* en inglés
(https://github.com/konradcinkusz/learning-to-count).

## Qué se mantiene y qué cambia

Se mantiene todo lo que no es lengua: el calendario, la escalera del
dinero (`MAX_EUROS`), las actividades y cuándo llega cada una
(`DESDE_SEMANA`), los dibujos, lo que se comprueba de cada actividad y
la clave, que la calcula el script. No hay una segunda copia de los
días: `content/english/q*.json` solo trae el texto de cada uno, y
`cargar_ingles` (en `tools/gen_economia.py`) lo pone encima del día de
`content/q*.json`:

- `historia`: la historia del día, que lee la niña o el niño (el lunes,
  con la palabra de la semana);
- y de la actividad, con su `tipo` (que tiene que ser el mismo), solo
  lo que se escribe a mano (`TEXTOS_ACTIVIDAD`): la `pregunta`, las
  `cajas` y las tarjetas (`cosas`) de *Sort*, las parejas (`pares`) de
  *Match*, las `frases` de *True or false?*, los `pasos` de *Put in
  order*, el nombre de las `tiendas` de *Compare*, los `apuntes` de
  *Money in and out*, el `texto` de *Word problem*, lo que va delante
  del hueco en *Share* (`cada`), y el `prompt` y la `checklist` de
  *Draw* y *Look back*.

Y cada uno, **igual que en español, en inglés**: las mismas tarjetas,
en el mismo orden y en las mismas cajas; las mismas verdades y las
mismas mentiras; las tiendas, con los mismos precios; los apuntes, con
las mismas cantidades; una `pregunta` o un `cada`, si y solo si los
lleva el día en español. `cargar_ingles` lo comprueba todo (`_forma`: el
mismo valor, sin los textos), y así las dos páginas son la misma
también cuando se barajan: las tarjetas, las parejas y los pasos se
mezclan con `random.Random(día)`, y con lo mismo en el mismo sitio
salen igual en los dos cuadernos.

Además, cada semana tiene su palabra en inglés (`semanas`, en
`content/english/q*.json`: la palabra, lo que quiere decir y sus
formas), con las mismas comprobaciones que en español: la dice la
historia del lunes, no se repite, y va a *My economics dictionary*, por
orden alfabético.

Lo demás que se lee en la página sale de `tools/idiomas.py` (los
nombres de las cosas, los temas de cada semana, cómo se escribe el
dinero, y el enunciado, la instrucción, lo que se completa y la clave
de cada actividad), de `lang/en.tex` (los títulos de las cajas, la
cabecera, la portada, lo que dicen las etiquetas de precio, las monedas
y los billetes: `\importe`) y de `frontmatter/english/` y
`backmatter/english/` (las páginas para el adulto, la clave, el
diccionario y el diploma). El español es `ESPANOL`, en el mismo
fichero, y lo que genera es, letra por letra, lo que generaba el script
antes de que hubiera un cuaderno en inglés.

## El inglés

**Británico**, como *First Numbers*, *Read and Draw* y *First Words*:
Mum, biscuits, sweets, a rubber para borrar, the pavement, pocket
money, a shop, the till, break time.

Lo que es de aquí se queda como en esos cuadernos: los nombres (Lucía,
Dani, Toby, Grandma Rosa; Sofía y Hugo, del Club de la Lupa -- *the
Magnifying Glass Club* --; Marta, la maestra; Paco, el conserje; Tomás,
el bibliotecario; Pedro y su gata Luna; en verano, Andrés, su gato
Bigotes y Martín), el roscón, los churros, las torrijas, las pesetas, la
fiesta del pueblo. Y el dinero son **euros**, como en español: Lucía
vive en España. En inglés, el símbolo va **delante** del número, y
pegado: €5, como £5 -- también en las etiquetas de precio, en las
monedas y en los billetes (`\importe`, en `lang/en.tex`) --, y el
script no deja escribir "5 €" ni "€ 5" en ningún texto en inglés
(`comprobar_euros_ingles`). Lo que se completa dice *euros* ("Total: [ ]
euros", "I have [ ] euros left"), como en *First Numbers*.

Las palabras de la semana son las de la economía, a la altura de una
niña de ocho años: *value*, *barter* (que en la página se explica con
*swap*, la palabra de todos los días), *money*, *scarcity*, *taxes*,
*loan*, *reuse*, *need* (y lo que no hace falta, *a want*), *savings*,
*reward*, *price*, *team*, *gift*...

## Las comprobaciones

Las mismas, en los dos cuadernos: `python3 tools/gen_economia.py
--check` valida y genera los dos; `make all-formats` compila los cuatro
PDF (color y blanco y negro de cada uno) y comprueba el log y que cada
día ocupa una página, y el día 1 la página 5 (también en inglés: las
páginas para el adulto tienen que seguir cabiendo en una cada una). El
CI hace lo mismo, con un job por PDF.

## Las fases

Como *Aprendo economía*, un PR por fase, cada uno en verde antes de
fusionarse. `DIAS_ESCRITOS_INGLES`, en `tools/gen_economia.py`, dice
cuántos días están escritos.

1. **El motor en dos lenguas y el otoño** (días 1--65):
   `tools/idiomas.py`, `cargar_ingles`, `lang/en.tex`, `english.tex`,
   las páginas para el adulto y el texto de los 65 días, con sus 13
   palabras. Además, un cuaderno de prueba con los 260 días (con el
   texto en español de relleno) para ver cómo quedan en inglés todas
   las actividades, también las que llegan después: *Choose*,
   *Compare* y *Money in and out*. **Hecho.**
2. **El invierno y la primavera** (días 66--195), con sus 26 palabras,
   de *choose* a *sell*. **Hecho.**
3. **El verano** (días 196--260), y publicarlo: la página de descarga y
   Pages con los cuatro PDF.
