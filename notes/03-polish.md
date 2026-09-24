# «Poznaję ekonomię» — el cuaderno en polaco

*Aprendo economía* en polaco, **página a página**, como *First
Economics* en inglés: la misma historia, el mismo dibujo y la misma
actividad cada día -- con las mismas cosas, los mismos precios, el
mismo dinero y las mismas respuestas --, así que una niña o un niño
puede hacer el que quiera, o más de uno. Es para una familia que hable
polaco en casa, o para quien lo aprende, y es de la misma familia que
*Aprendo a leer* (https://github.com/konradcinkusz/learning-to-read) y
*Aprendo los números* (https://github.com/konradcinkusz/learning-to-count).

## El motor, en tres lenguas

El de *First Economics*, sin una segunda copia de los días:
`content/polish/q*.json` solo trae el texto de cada uno -- la
`historia` y, de la actividad, con su `tipo`, lo que se escribe a mano
(`TEXTOS_ACTIVIDAD`) --, y `cargar_traduccion` (en
`tools/gen_economia.py`) lo pone encima del día de `content/q*.json` y
lo comprueba todo, como en inglés (`_forma`: las mismas tarjetas, en el
mismo orden y en las mismas cajas; las mismas verdades; los mismos
precios y cantidades; una `pregunta` o un `cada`, si y solo si los
lleva el día en español). Ver "Qué se mantiene y qué cambia" en
[`02-english.md`](02-english.md).

Lo que cambia en el motor para que quepa una tercera lengua:

- `tools/gen_economia.py` genera cada cuaderno de un `Cuaderno`: su
  nombre, su lengua (`ESPANOL`, `INGLES`, `POLACO`, de
  `tools/idiomas.py`), su carpeta, su `lang/*.tex` y cuántos días
  están escritos (`DIAS_ESCRITOS_POLACO`, mientras se escribe).
  `APRENDO` es el español; `TRADUCCIONES`, *First Economics* y
  *Poznaję ekonomię*.
- `comprobar_euros(L, ...)`: cada lengua dice cómo **no** se escribe el
  euro (`L.euro_mal`) y por qué (`L.aviso_euro`).
- `preamble.tex`: `\booklang{polish}` lee `lang/pl.tex` y carga
  `babel` en polaco (con `\shorthandoff{"}`: el polaco de `babel`
  hace de `"` un atajo, y el cuaderno no lo usa).
- `lang/pl.tex`, `polish.tex`, `polish-bw.tex`, `body-polish.tex`, y
  `frontmatter/polish/` y `backmatter/polish/` (las páginas para el
  adulto, la clave, *Mój słowniczek ekonomiczny* y el diploma).

Lo generado para *Aprendo economía* y *First Economics* es, letra por
letra, lo que era antes.

## El polaco

Lo que se escribe con un número sale de `tools/idiomas.py`, y en polaco
el número decide la forma de la palabra: 1 lleva el singular (*1
muszelka*); 2, 3 y 4 (y 22, 23, 24..., pero no 12, 13 y 14), el
nominativo plural (*2 karty*); y los demás, el genitivo plural (*5
kart*, *12 ciastek*). `_grupo(n)` elige cuál, y cada cosa tiene sus
cuatro formas y su género (`objetos`: *karta, kartę, karty, kart*),
también en acusativo cuando se compra, se cambia o se reparte
(*Podziel 12 ciastek na 5 osób*, *Można zamienić 1 muszelkę na 2
karty*). Y lo que concuerda con el número: *zostaje 1* / *zostają 2*,
*tydzień* / *tygodnie* / *tygodni*.

Los personajes son los de siempre, y sus nombres se declinan: *Lucía*
(*Lucíi*, *Lucíę*, *Lucíą*), *Dani* (*Daniego*), *Hugo* (*Hugona*),
*Toby* (*Toby'ego*), *babcia Rosa*; los mayores, con *pan* y *pani*:
*pan Paco*, *pan Tomás*, *pan Pedro*, *pani Marta*. Lo que es de aquí
se queda (el roscón, los churros, las torrijas, las pesetas, la fiesta
del pueblo), y el dinero son **euros**: Lucía vive en España. Se
escribe como en español, detrás del número y con un espacio: 5 €, y el
script no deja escribir "€5", "€ 5" ni "5€" en ningún texto en polaco.
Las páginas para el adulto dicen que, si en casa se paga en złoty, es
una buena ocasión para hablar de que cada país tiene su dinero.

Lo que dice la niña o el niño no tiene género: *Wiem...*, *Umiem...*,
*Narysuj...*, y nunca un pasado en *-łem* / *-łam*. Las comillas son
las polacas, „así”, y *Mój słowniczek ekonomiczny* va por el orden del
alfabeto polaco (*a, ą, b, c, ć... ł... ś... ź, ż*).

Las palabras de la semana son las de la economía, a la altura de una
niña de ocho años: *wartość*, *handel wymienny* (que en la página se
explica con *wymiana*, la palabra de todos los días), *pieniądze*,
*niedobór*, *podatki*, *pożyczka*, *użyć ponownie*, *potrzeba* (y lo
que no hace falta, *zachcianka*), *oszczędności*, *nagroda*, *cena*,
*zespół*, *prezent*; en invierno, *wybierać*, *peseta*, *kilogram*
(con *kilo*, que es como se dice en la tienda), *produkować*, *dbać*,
*zasoby*, *porozumienie*, *budżet*, *koszt*, *usługa*, *naprawiać*,
*cel*, *przyroda*; y en primavera, *euro* (que en polaco no se
declina), *wydatek*, *warsztat*, *pensja*, *wymiana* (ahora sí la
palabra: cambiar cosas entre varios, como en el Día del Libro),
*sklep*, *odpowiedzialność*, *czas*, *skarbonka*, *łańcuch*,
*konsumować*, *bank*, *sprzedawać*...

## Las comprobaciones

Las mismas en los tres cuadernos: `python3 tools/gen_economia.py
--check` valida y genera los tres; `make polish` compila y comprueba el
cuaderno en polaco, y `make all-formats`, los seis PDF (color y blanco
y negro de cada uno): el log, que cada día ocupa una página, y el día 1
la página 5 (las páginas para el adulto tienen que seguir cabiendo en
una cada una, también en polaco). El CI hace lo mismo, con un job por
PDF.

## Las fases

Como *First Economics*, un PR por fase, cada uno en verde antes de
fusionarse. `DIAS_ESCRITOS_POLACO`, en `tools/gen_economia.py`, dice
cuántos días están escritos.

1. **El motor en tres lenguas y el otoño** (días 1--65):
   `POLACO` en `tools/idiomas.py`, `Cuaderno` y `cargar_traduccion`,
   `lang/pl.tex`, `polish.tex`, las páginas para el adulto y el texto
   de los 65 días, con sus 13 palabras, de *wartość* a *prezent*.
   **Hecho.**
2. **El invierno y la primavera** (días 66--195), con sus 26 palabras,
   de *wybierać* a *sprzedawać*. **Hecho.**
3. **El verano** (días 196--260), con sus 13 palabras, hasta
   *ekonomia*, y publicarlo: el cuaderno entero
   (`DIAS_ESCRITOS_POLACO = None`), la página de descarga y Pages con
   los seis PDF.
