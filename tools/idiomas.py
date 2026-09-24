"""Las dos lenguas del cuaderno de economía.

tools/gen_economia.py genera dos cuadernos que son, página a página, el
mismo: "Aprendo economía" (main.tex), en español, y "First Economics"
(english.tex), en inglés británico, como "First Numbers" es "Aprendo los
números" en inglés (https://github.com/konradcinkusz/learning-to-count).
Comparten todo lo que no es lengua -- el calendario, la escalera del
dinero, los dibujos, las actividades y lo que se comprueba de cada una
--, y lo que cambia de uno a otro está aquí, en un solo sitio:

  - cómo se llaman las cosas, con su artículo ("un lápiz", "una canica";
    "a pencil", "an ice cream"): el dibujo es el mismo (OBJETOS, en
    tools/gen_economia.py);
  - cómo se escribe el dinero: "5 €" en español y "€5" en inglés;
  - el tema de cada semana y el nombre de cada medalla;
  - y el enunciado, la instrucción, lo que se completa y la entrada de la
    clave de cada actividad, que tools/gen_economia.py compone con las
    cosas, los precios y el dinero de cada día ("Compras un lápiz y un
    libro. ¿Cuánto pagas?", "You buy a pencil and a book. How much do
    you pay?").

Lo que la página dice siempre igual (los títulos de las cajas, la
cabecera de cada día, la portada) no está aquí, sino en lang/es.tex y
lang/en.tex.

Cada lengua es un objeto con los mismos métodos: ESPANOL e INGLES, más
abajo. Los métodos de ESPANOL devuelven, letra por letra, lo que
escribía tools/gen_economia.py antes de que hubiera un cuaderno en
inglés.
"""

from string import Template


# La página de medalla del final de cada trimestre (T1-T3): de una lengua
# a otra solo cambian "días" y "páginas" (el título y el ánimo están en
# lang/es.tex y lang/en.tex).
_MEDALLA = r"""\begin{center}
\vspace*{3cm}
\medalla{$dia}

\vspace{10mm}
{\fontsize{34}{40}\selectfont\bfseries\color{colorLectura}\lblMedalla{$estacion}}\\[8mm]
{\Large $dia\ %s, $dia\ %s.}\\[12mm]
{\Large \lblMedallaAnimo}
\end{center}
\vspace*{\fill}
\newpage
"""


class Espanol:
    codigo = "es"

    # Los temas de cada semana: los de "Leo con lupa" (content/lupa/ en
    # "Aprendo a leer"), para que quien lleve los dos cuadernos se
    # encuentre la misma semana en los dos. El tema de cada día tiene que
    # ser el de su semana.
    temas = [
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

    nombre_medalla = {1: "Otoño", 2: "Invierno", 3: "Primavera"}
    plantilla_medalla = Template(_MEDALLA % ("días", "páginas"))

    # ----------------------------------------------------------------
    # Las cosas: singular, plural y género -- el enunciado se compone con
    # ellos ("Si 1 concha vale 2 cromos, ¿cuántos cromos te dan por 3
    # conchas?").
    # ----------------------------------------------------------------
    objetos = {
        # Las de este cuaderno (diagrams/economia.tex).
        "lupa": ("lupa", "lupas", "f"),
        "cromo": ("cromo", "cromos", "m"),
        "canica": ("canica", "canicas", "f"),
        "hucha": ("hucha", "huchas", "f"),
        "entrada": ("entrada", "entradas", "f"),
        "uva": ("uva", "uvas", "f"),
        "racimo": ("racimo de uvas", "racimos de uvas", "m"),
        "roscon": ("roscón", "roscones", "m"),
        "carta": ("carta", "cartas", "f"),
        "telescopio": ("telescopio", "telescopios", "m"),
        "antifaz": ("antifaz", "antifaces", "m"),
        "mapa": ("mapa", "mapas", "m"),
        "leche": ("cartón de leche", "cartones de leche", "m"),
        "miel": ("tarro de miel", "tarros de miel", "m"),
        "tortuga": ("tortuga", "tortugas", "f"),
        "limon": ("limón", "limones", "m"),
        "caracol": ("caracol", "caracoles", "m"),
        # Las de "Aprendo los números" (diagrams/objetos.tex).
        "manzana": ("manzana", "manzanas", "f"),
        "pelota": ("pelota", "pelotas", "f"),
        "hueso": ("hueso", "huesos", "m"),
        "sol": ("sol", "soles", "m"),
        "toby": ("perro", "perros", "m"),
        "huella": ("huella", "huellas", "f"),
        "globo": ("globo", "globos", "m"),
        "estrella": ("estrella", "estrellas", "f"),
        "hoja": ("hoja", "hojas", "f"),
        "corazon": ("corazón", "corazones", "m"),
        "caramelo": ("caramelo", "caramelos", "m"),
        "pez": ("pez", "peces", "m"),
        "lapiz": ("lápiz", "lápices", "m"),
        "libro": ("libro", "libros", "m"),
        "galleta": ("galleta", "galletas", "f"),
        "castana": ("castaña", "castañas", "f"),
        "cesta": ("cesta", "cestas", "f"),
        "regalo": ("regalo", "regalos", "m"),
        "paraguas": ("paraguas", "paraguas", "m"),
        "arbol": ("árbol", "árboles", "m"),
        "coche": ("coche", "coches", "m"),
        "trex": ("dinosaurio", "dinosaurios", "m"),
        "huevo": ("huevo", "huevos", "m"),
        "gato": ("gato", "gatos", "m"),
        "mochila": ("mochila", "mochilas", "f"),
        "plato": ("plato", "platos", "m"),
        "mandarina": ("mandarina", "mandarinas", "f"),
        "osito": ("osito", "ositos", "m"),
        "flor": ("flor", "flores", "f"),
        "boton": ("botón", "botones", "m"),
        "fresa": ("fresa", "fresas", "f"),
        "piruleta": ("piruleta", "piruletas", "f"),
        "ovillo": ("ovillo", "ovillos", "m"),
        "bufanda": ("bufanda", "bufandas", "f"),
        "gorro": ("gorro", "gorros", "m"),
        "maceta": ("maceta", "macetas", "f"),
        "bici": ("bici", "bicis", "f"),
        "tarta": ("tarta", "tartas", "f"),
        "abeja": ("abeja", "abejas", "f"),
        "moneda": ("moneda", "monedas", "f"),
        "torrija": ("torrija", "torrijas", "f"),
        "zanahoria": ("zanahoria", "zanahorias", "f"),
        "tomate": ("tomate", "tomates", "m"),
        "pan": ("pan", "panes", "m"),
        "lechuga": ("lechuga", "lechugas", "f"),
        "maleta": ("maleta", "maletas", "f"),
        "helado": ("helado", "helados", "m"),
        "concha": ("concha", "conchas", "f"),
        "cubo": ("cubo", "cubos", "m"),
        "churro": ("churro", "churros", "m"),
        "corona": ("corona", "coronas", "f"),
        "muneco": ("muñeco de nieve", "muñecos de nieve", "m"),
        "pajaro": ("pájaro", "pájaros", "m"),
        "paloma": ("paloma", "palomas", "f"),
        "vela": ("vela", "velas", "f"),
        "reloj": ("reloj", "relojes", "m"),
        "regadera": ("regadera", "regaderas", "f"),
        "rueda": ("rueda", "ruedas", "f"),
        "cometa": ("cometa", "cometas", "f"),
        "copo": ("copo de nieve", "copos de nieve", "m"),
        "tarjeta": ("tarjeta", "tarjetas", "f"),
        "nube": ("nube", "nubes", "f"),
        "gota": ("gota", "gotas", "f"),
        "rosa": ("rosa", "rosas", "f"),
        "brote": ("brote", "brotes", "m"),
        "pollito": ("pollito", "pollitos", "m"),
        "mano": ("mano", "manos", "f"),
        "gorrofiesta": ("gorro de fiesta", "gorros de fiesta", "m"),
    }

    def cosa(self, objeto, n):
        singular, plural, _ = self.objetos[objeto]
        return singular if n == 1 else plural

    def femenino(self, objeto):
        return self.objetos[objeto][2] == "f"

    def un(self, objeto):
        """"un lápiz", "una canica"."""
        return ("una " if self.femenino(objeto) else "un ") + self.cosa(objeto, 1)

    def el(self, objeto):
        """"el lápiz", "la canica"."""
        return ("la " if self.femenino(objeto) else "el ") + self.cosa(objeto, 1)

    @staticmethod
    def mayuscula(texto):
        return texto.capitalize()

    # ----------------------------------------------------------------
    # El dinero
    # ----------------------------------------------------------------
    @staticmethod
    def euros(n):
        """"5 €" (en el texto, escapar() ya no los deja separarse)."""
        return f"{n} €"

    @staticmethod
    def euros_tabla(n):
        """"5~€": en una casilla del cuaderno de cuentas."""
        return f"{n}~€"

    @staticmethod
    def sobra(n):
        """"no sobra nada", "sobra 1 €", "sobran 3 €"."""
        return "no sobra nada" if n == 0 else "sobra 1 €" if n == 1 else f"sobran {n} €"

    @staticmethod
    def enumerar(cosas, frases=False):
        """"un paraguas, una cuchara y una escoba"; si son frases enteras,
        cada una entre comillas y separadas por barras: «...» / «...»."""
        cosas = [c.rstrip(".") for c in cosas]
        if frases:
            return " / ".join(f"«{c}»" for c in cosas)
        if len(cosas) == 1:
            return cosas[0]
        return ", ".join(cosas[:-1]) + " y " + cosas[-1]

    def describir_dinero(self, valores):
        """"un billete de 10 €", "un billete de 5 € y dos monedas de 2 €"."""
        cuantos = {2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis"}
        partes = []
        for v in sorted(set(valores), reverse=True):
            k = valores.count(v)
            cosa = "billete" if v >= 5 else "moneda"
            uno = "un" if v >= 5 else "una"
            partes.append(f"{uno if k == 1 else cuantos[k]} {cosa}{'' if k == 1 else 's'} de {v} €")
        return partes[0] if len(partes) == 1 else self.enumerar(partes)

    @staticmethod
    def semana_hucha(n):
        """Debajo de cada casilla de "La hucha": "1.ª" (la primera semana)."""
        return f"{n}.ª"

    @staticmethod
    def orden_alfabetico(palabra):
        """Para ordenar el diccionario: sin tildes ("ahorro" antes que
        "árbol")."""
        return palabra.translate(str.maketrans("áéíóúü", "aeiouu"))

    # ----------------------------------------------------------------
    # Las actividades: lo que se lee en cada una. Devuelven el enunciado
    # (lo grande; el que se usa si el JSON no trae 'pregunta'), la
    # instrucción (la letra pequeña, que lee el adulto), lo que se
    # completa (con \huecoRespuesta) y el texto de la clave, según lo que
    # lleve cada actividad.
    # ----------------------------------------------------------------
    def clasifica(self, cajas, cosas):
        # Tarjetas con frases enteras (empiezan en mayúscula), entre comillas.
        frases = any(c[0][0].isupper() or "," in c[0] for c in cosas)
        return ("Une cada cosa con su caja.",
                "Lee cada tarjeta, y traza una línea desde su punto hasta la caja que le toca.",
                " ".join(f"{cajas[i]}: {self.enumerar([c[0] for c in cosas if c[1] == i], frases)}."
                         for i in (0, 1)))

    def une(self, pares):
        return ("Une cada una con la suya.",
                "Lee las dos columnas, y traza una línea desde cada punto de la izquierda "
                "hasta el punto de la derecha que le toca.",
                "; ".join(f"{p[0]} → {p[1]}" for p in pares))

    def vf(self, frases):
        return ("¿Es verdad o es mentira?",
                "Lee cada frase, y rodea la V si es verdad, o la F si es mentira (falso).",
                ", ".join(f"{i}: {'V' if f[1] else 'F'}" for i, f in enumerate(frases, 1)))

    def trueque(self, oa, na, ob, nb, de, n, otra, respuesta):
        """na cosas oa valen nb cosas ob: ¿cuántas `otra` te dan por n `de`?"""
        vale = "vale" if na == 1 else "valen"
        cuantas = "cuántas" if self.femenino(otra) else "cuántos"
        return (f"Si {na} {self.cosa(oa, na)} {vale} {nb} {self.cosa(ob, nb)}, "
                f"¿{cuantas} {self.cosa(otra, 2)} te dan por {n} {self.cosa(de, n)}?",
                "Mira el cambio de arriba. Si hace falta, dibuja las cosas, y escribe "
                "en el hueco cuántas te dan.",
                f"{respuesta} {self.cosa(otra, respuesta)}")

    def dinero(self, total):
        return ("¿Cuánto dinero hay?",
                "Cuenta primero los billetes y después las monedas, y escribe cuántos euros hay en total.",
                "Hay \\huecoRespuesta\\ €",
                f"{total} €")

    # "A cada uno", o lo que diga el JSON cuando se reparte entre otras
    # cosas: "En cada una" (estanterías), "Cada una" (mamás).
    cada_uno = "A cada uno"

    def reparte(self, objeto, total, entre, comida, cada_uno, cada_uno_tex, cada, sobran):
        """Se reparten `total` cosas entre `entre`: a cada uno le tocan
        `cada`, y sobran `sobran`. `cada_uno` es lo que va delante de su
        hueco ("A cada uno"), y `cada_uno_tex`, lo mismo, ya escapado."""
        f = self.femenino(objeto)
        return (f"Reparte {total} {self.cosa(objeto, total)} entre {entre}. "
                f"¿{'Cuántas' if f else 'Cuántos'} le tocan a cada uno? "
                f"¿Sobra {'alguna' if f else 'alguno'}?",
                f"Dibuja en cada {'plato' if comida else 'recuadro'} lo que le toca, de uno en uno, hasta que ya no "
                "se pueda más: lo que no se puede repartir, sobra.",
                f"{{\\fontsize{{26}}{{32}}\\selectfont {cada_uno_tex}: \\huecoRespuesta[20mm]\\hspace{{10mm}}"
                "Sobran: \\huecoRespuesta[20mm]}",
                f"{cada} {cada_uno[0].lower() + cada_uno[1:]}; "
                + ("no sobra nada" if not sobran else "sobra 1" if sobran == 1 else f"sobran {sobran}"))

    def compra(self, compra, precios, total):
        return (f"Compras {self.enumerar([self.un(c) for c in compra])}. ¿Cuánto pagas?",
                "Busca el precio de cada cosa que se compra, súmalos, y escribe cuánto se paga en total.",
                "Total: \\huecoRespuesta\\ €",
                " + ".join(str(precios[c]) for c in compra) + f" = {total} €")

    def llega(self, tengo, si):
        """Se tienen `tengo` euros, y llega para las cosas de `si`."""
        return (f"Tienes {tengo} €. Rodea lo que puedes comprar.",
                "Mira el precio de cada cosa: si cuesta lo mismo o menos que lo que tienes, te llega.",
                f"con {tengo} € llega para {self.enumerar([self.un(o) for o in si])}")

    def cambio(self, objeto, precio, paga, pago):
        """`objeto` cuesta `precio`, y se paga con las monedas y los
        billetes de `paga`, que suman `pago`."""
        return (f"{self.mayuscula(self.un(objeto))} cuesta {precio} €. Pagas con "
                f"{self.describir_dinero(paga)}. ¿Cuánto te devuelven?",
                "La vuelta es lo que te devuelven: lo que das, menos lo que cuesta. Si ayuda, "
                "cuenta desde el precio hasta lo que das.",
                "Te devuelven \\huecoRespuesta\\ €",
                f"{pago} − {precio} = {pago - precio} €")

    def problema(self):
        return "Lee el problema despacio. Dibújalo en el recuadro, si ayuda, y escribe la cuenta y el resultado."

    def botes(self, falta, cantidad):
        """En el bote `falta` (0 ahorrar, 1 gastar, 2 compartir) falta
        `cantidad`."""
        return ("Lo que hay en los tres botes, junto, es todo el dinero. Escribe en el bote vacío lo que falta.",
                f"{['ahorrar', 'gastar', 'compartir'][falta]}: {cantidad} €")

    def hucha(self, tiene, cada, meta, semanas):
        empieza = f"Tienes {tiene} € en la hucha." if tiene else "Tu hucha está vacía."
        return (f"{empieza} Si ahorras {cada} € cada semana, ¿cuántas semanas tardas en tener {meta} €?",
                "Apunta en cada casilla lo que hay en la hucha al final de cada semana, hasta llegar "
                "a la meta. Después, cuenta las semanas.",
                "\\huecoRespuesta\\ semanas",
                f"{semanas} semanas (" + ", ".join(f"{tiene + cada * k}" for k in range(1, semanas + 1)) + " €)")

    def ordena(self, numeros):
        """`numeros`: el número de cada paso, de arriba abajo."""
        return ("¿En qué orden va? Escribe 1, 2, 3...",
                "Lee todos los pasos, y escribe en cada casilla su número: 1 el primero, 2 el segundo...",
                "de arriba abajo: " + ", ".join(str(x) for x in numeros))

    def elige(self, tengo, cosas):
        if len(cosas) == 2:
            dos = "las dos" if all(self.femenino(o) for o, _ in cosas) else "los dos"
            defecto = (f"Tienes {tengo} €: te llega para {self.un(cosas[0][0])} o para {self.un(cosas[1][0])}, "
                       f"pero no para {dos}. ¿Qué eliges?")
        else:
            defecto = f"Tienes {tengo} €: te llega para una de estas cosas, pero no para dos. ¿Cuál eliges?"
        return (defecto,
                "Rodea lo que eliges y tacha lo que dejas: elegir una cosa es dejar otra. "
                "Después, escribe cuánto dinero te sobra.",
                "Me sobran \\huecoRespuesta\\ €",
                "vale cualquiera: " + "; ".join(f"{self.el(o)}, {self.sobra(tengo - p)}" for o, p in cosas))

    def compara(self, barata, cara):
        """`barata` y `cara`: las dos tiendas, [nombre, precio]."""
        return ("Mira el precio en las dos tiendas. Rodea la tienda donde es más barato, y escribe "
                "cuánto te ahorras: lo que va de un precio al otro.",
                "Me ahorro \\huecoRespuesta\\ €",
                f"«{barata[0]}», {barata[1]} € y no {cara[1]} €: te ahorras {cara[1] - barata[1]} €")

    def cuentas(self, quedas):
        """`quedas`: lo que queda después de cada apunte."""
        return ("¿Cuánto queda después de cada apunte?",
                "Empieza por lo que hay al principio. Si entra dinero, se suma; si sale, se resta. "
                "Escribe en cada casilla lo que queda.",
                "queda: " + ", ".join(str(q) for q in quedas) + f" €; al final, {quedas[-1]} €")


class Ingles(Espanol):
    """"First Economics": el mismo cuaderno, en inglés británico -- como
    "First Numbers", y "Read and Draw" y "First Words" de "Aprendo a
    leer" (Mum, biscuits, sweets, a shop, pocket money). Los personajes y
    lo que es de aquí se quedan como en esos cuadernos: Lucía, Grandma
    Rosa, Marta, Paco y Tomás; el roscón, los churros, las torrijas, las
    pesetas y los euros, escritos a la inglesa: €5."""

    codigo = "en"

    temas = [
        "Grandma's magnifying glass", "A new classmate", "The Magnifying Glass Club",
        "The case of the biscuits", "Footprints in the cement", "The Tuesday leaf",
        "Noises in the attic", "The shopping list", "Eight years old",
        "Where is Luna?", "The dinosaur museum", "The Christmas play",
        "Reader X unmasked!",
        "The walking Kings", "Christmas Eve and the map", "The twelve grapes",
        "The roscón de Reyes", "An early-rising snowman", "Hugo's periscope",
        "Peace Day", "Dad's birthday", "Carnival", "A letter from the village",
        "The droopy plants", "The planetarium", "The nest in the garden",
        "A photo from twenty-five years ago", "Torrijas, on her own this time",
        "The flat tyre", "Interviewing Paco", "World Book Day",
        "The old plan", "Rayo runs away", "Mother's Day",
        "Dani turns six", "The bees in the park", "The school farm",
        "Here's the time capsule!", "The end-of-year party",
        "The suitcase", "Back in the village", "Ten steps", "Lucía's diary",
        "Andrés's bees", "The night of the shooting stars",
        "A letter from Hugo", "The village fiesta", "Rosa's treasure!",
        "Dani and Martín's map", "Back to the city",
        "Dani goes to big school", "Back to school",
    ]

    nombre_medalla = {1: "Autumn", 2: "Winter", 3: "Spring"}
    plantilla_medalla = Template(_MEDALLA % ("days", "pages"))

    # Singular y plural (el género no hace falta).
    objetos = {
        "lupa": ("magnifying glass", "magnifying glasses"),
        "cromo": ("card", "cards"),
        "canica": ("marble", "marbles"),
        "hucha": ("piggy bank", "piggy banks"),
        "entrada": ("ticket", "tickets"),
        "uva": ("grape", "grapes"),
        "racimo": ("bunch of grapes", "bunches of grapes"),
        "roscon": ("roscón", "roscones"),
        "carta": ("letter", "letters"),
        "telescopio": ("telescope", "telescopes"),
        "antifaz": ("mask", "masks"),
        "mapa": ("map", "maps"),
        "leche": ("carton of milk", "cartons of milk"),
        "miel": ("jar of honey", "jars of honey"),
        "tortuga": ("tortoise", "tortoises"),
        "limon": ("lemon", "lemons"),
        "caracol": ("snail", "snails"),
        "manzana": ("apple", "apples"),
        "pelota": ("ball", "balls"),
        "hueso": ("bone", "bones"),
        "sol": ("sun", "suns"),
        "toby": ("dog", "dogs"),
        "huella": ("paw print", "paw prints"),
        "globo": ("balloon", "balloons"),
        "estrella": ("star", "stars"),
        "hoja": ("leaf", "leaves"),
        "corazon": ("heart", "hearts"),
        "caramelo": ("sweet", "sweets"),
        "pez": ("fish", "fish"),
        "lapiz": ("pencil", "pencils"),
        "libro": ("book", "books"),
        "galleta": ("biscuit", "biscuits"),
        "castana": ("chestnut", "chestnuts"),
        "cesta": ("basket", "baskets"),
        "regalo": ("present", "presents"),
        "paraguas": ("umbrella", "umbrellas"),
        "arbol": ("tree", "trees"),
        "coche": ("car", "cars"),
        "trex": ("dinosaur", "dinosaurs"),
        "huevo": ("egg", "eggs"),
        "gato": ("cat", "cats"),
        "mochila": ("school bag", "school bags"),
        "plato": ("plate", "plates"),
        "mandarina": ("tangerine", "tangerines"),
        "osito": ("teddy bear", "teddy bears"),
        "flor": ("flower", "flowers"),
        "boton": ("button", "buttons"),
        "fresa": ("strawberry", "strawberries"),
        "piruleta": ("lollipop", "lollipops"),
        "ovillo": ("ball of wool", "balls of wool"),
        "bufanda": ("scarf", "scarves"),
        "gorro": ("woolly hat", "woolly hats"),
        "maceta": ("flowerpot", "flowerpots"),
        "bici": ("bike", "bikes"),
        "tarta": ("cake", "cakes"),
        "abeja": ("bee", "bees"),
        "moneda": ("coin", "coins"),
        "torrija": ("torrija", "torrijas"),
        "zanahoria": ("carrot", "carrots"),
        "tomate": ("tomato", "tomatoes"),
        "pan": ("loaf", "loaves"),
        "lechuga": ("lettuce", "lettuces"),
        "maleta": ("suitcase", "suitcases"),
        "helado": ("ice cream", "ice creams"),
        "concha": ("shell", "shells"),
        "cubo": ("bucket", "buckets"),
        "churro": ("churro", "churros"),
        "corona": ("crown", "crowns"),
        "muneco": ("snowman", "snowmen"),
        "pajaro": ("bird", "birds"),
        "paloma": ("dove", "doves"),
        "vela": ("candle", "candles"),
        "reloj": ("clock", "clocks"),
        "regadera": ("watering can", "watering cans"),
        "rueda": ("wheel", "wheels"),
        "cometa": ("kite", "kites"),
        "copo": ("snowflake", "snowflakes"),
        "tarjeta": ("card", "cards"),
        "nube": ("cloud", "clouds"),
        "gota": ("raindrop", "raindrops"),
        "rosa": ("rose", "roses"),
        "brote": ("shoot", "shoots"),
        "pollito": ("chick", "chicks"),
        "mano": ("hand", "hands"),
        "gorrofiesta": ("party hat", "party hats"),
    }

    def cosa(self, objeto, n):
        singular, plural = self.objetos[objeto]
        return singular if n == 1 else plural

    def femenino(self, objeto):
        return False

    def un(self, objeto):
        """"a pencil", "an ice cream"."""
        nombre = self.cosa(objeto, 1)
        return ("an " if nombre[0] in "aeiou" else "a ") + nombre

    def el(self, objeto):
        return "the " + self.cosa(objeto, 1)

    @staticmethod
    def mayuscula(texto):
        # Solo la primera letra: .capitalize() haría "A t-shirt" de "a T-shirt".
        return texto[:1].upper() + texto[1:]

    @staticmethod
    def euros(n):
        """"€5": el símbolo, delante, y pegado al número."""
        return f"€{n}"

    euros_tabla = euros

    @staticmethod
    def sobra(n):
        return "nothing left" if n == 0 else f"€{n} left"

    @staticmethod
    def enumerar(cosas, frases=False, y="and"):
        """"an umbrella, a spoon and a broom" (sin la coma de Oxford, como
        en "First Numbers"); las frases, entre comillas: “...” / “...”."""
        cosas = [c.rstrip(".") for c in cosas]
        if frases:
            return " / ".join(f"“{c}”" for c in cosas)
        if len(cosas) == 1:
            return cosas[0]
        return ", ".join(cosas[:-1]) + f" {y} " + cosas[-1]

    def describir_dinero(self, valores):
        """"a €10 note", "a €5 note and two €2 coins"."""
        cuantos = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
        partes = []
        for v in sorted(set(valores), reverse=True):
            k = valores.count(v)
            cosa = "note" if v >= 5 else "coin"
            partes.append(f"{'a' if k == 1 else cuantos[k]} €{v} {cosa}{'' if k == 1 else 's'}")
        return partes[0] if len(partes) == 1 else self.enumerar(partes)

    @staticmethod
    def semana_hucha(n):
        """"1st", "2nd", "3rd", "4th"..."""
        return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"

    @staticmethod
    def orden_alfabetico(palabra):
        return palabra

    # Las instrucciones le hablan a la niña o al niño, como en español (y
    # las lee un adulto, si hace falta): no empiezan por "A grown-up reads
    # out...", como en "First Numbers", porque aquí la historia y el
    # enunciado ya los lee ella o él.
    def clasifica(self, cajas, cosas):
        # Frases enteras: las que terminan en punto (o llevan coma). En
        # inglés no basta con la mayúscula: "Lucía's bike" no es una frase.
        frases = any(c[0][-1] in ".!?" or "," in c[0] for c in cosas)
        return ("Match each thing to its box.",
                "Read each card, and draw a line from its dot to the box it belongs in.",
                " ".join(f"{cajas[i]}: {self.enumerar([c[0] for c in cosas if c[1] == i], frases)}."
                         for i in (0, 1)))

    def une(self, pares):
        return ("Match each one to its pair.",
                "Read both columns, and draw a line from each dot on the left to the dot on "
                "the right that goes with it.",
                "; ".join(f"{p[0]} → {p[1]}" for p in pares))

    def vf(self, frases):
        return ("True or false?",
                "Read each sentence, and circle T if it is true, or F if it is false.",
                ", ".join(f"{i}: {'T' if f[1] else 'F'}" for i, f in enumerate(frases, 1)))

    def trueque(self, oa, na, ob, nb, de, n, otra, respuesta):
        return (f"If {na} {self.cosa(oa, na)} {'is' if na == 1 else 'are'} worth {nb} {self.cosa(ob, nb)}, "
                f"how many {self.cosa(otra, 2)} do you get for {n} {self.cosa(de, n)}?",
                "Look at the swap at the top. If it helps, draw the things, and write in the box "
                "how many you get.",
                f"{respuesta} {self.cosa(otra, respuesta)}")

    def dinero(self, total):
        return ("How much money is there?",
                "Count the notes first and then the coins, and write how many euros there are altogether.",
                "\\huecoRespuesta\\ euros",
                f"€{total}")

    cada_uno = "Each one"

    def reparte(self, objeto, total, entre, comida, cada_uno, cada_uno_tex, cada, sobran):
        return (f"Share {total} {self.cosa(objeto, total)} between {entre}. How many does each one get? "
                "Are there any left over?",
                f"Draw what each one gets {'on each plate' if comida else 'in each box'}, one at a time, "
                "until you can't share any more: what can't be shared is left over.",
                f"{{\\fontsize{{26}}{{32}}\\selectfont {cada_uno_tex}: \\huecoRespuesta[20mm]\\hspace{{10mm}}"
                "Left over: \\huecoRespuesta[20mm]}",
                f"{cada_uno}: {cada}; " + ("nothing left over" if not sobran else f"{sobran} left over"))

    def compra(self, compra, precios, total):
        return (f"You buy {self.enumerar([self.un(c) for c in compra])}. How much do you pay?",
                "Find the price of each thing you buy, add them up, and write how much you pay altogether.",
                "Total: \\huecoRespuesta\\ euros",
                " + ".join(f"€{precios[c]}" for c in compra) + f" = €{total}")

    def llega(self, tengo, si):
        # "or": llega para cada una, no para todas juntas.
        return (f"You have €{tengo}. Circle what you can buy.",
                "Look at the price of each thing: if it costs the same as what you have, or less, "
                "you can afford it.",
                f"with €{tengo} you can afford {self.enumerar([self.un(o) for o in si], y='or')}")

    def cambio(self, objeto, precio, paga, pago):
        return (f"{self.mayuscula(self.un(objeto))} costs €{precio}. You pay with "
                f"{self.describir_dinero(paga)}. How much change do you get?",
                "Your change is what you get back: what you pay, take away what it costs. If it helps, "
                "count on from the price to what you pay.",
                "Change: \\huecoRespuesta\\ euros",
                f"€{pago} − €{precio} = €{pago - precio}")

    def problema(self):
        return "Read the problem slowly. Draw it in the box if it helps, and write the calculation and the answer."

    def botes(self, falta, cantidad):
        return ("Together, the three jars hold all the money. Write what is missing in the empty jar.",
                f"{['save', 'spend', 'share'][falta]}: €{cantidad}")

    def hucha(self, tiene, cada, meta, semanas):
        empieza = f"You have €{tiene} in your piggy bank." if tiene else "Your piggy bank is empty."
        return (f"{empieza} If you save €{cada} every week, how many weeks will it take to have €{meta}?",
                "In each box, write how much is in the piggy bank at the end of each week, until you "
                "reach your goal. Then count the weeks.",
                "\\huecoRespuesta\\ weeks",
                f"{semanas} {'week' if semanas == 1 else 'weeks'} ("
                + ", ".join(f"€{tiene + cada * k}" for k in range(1, semanas + 1)) + ")")

    def ordena(self, numeros):
        return ("What is the right order? Write 1, 2, 3...",
                "Read all the steps, and write its number in each box: 1 for the first, 2 for the second...",
                "top to bottom: " + ", ".join(str(x) for x in numeros))

    def elige(self, tengo, cosas):
        if len(cosas) == 2:
            defecto = (f"You have €{tengo}: you can afford {self.un(cosas[0][0])} or {self.un(cosas[1][0])}, "
                       "but not both. Which do you choose?")
        else:
            defecto = f"You have €{tengo}: you can afford one of these things, but not two. Which do you choose?"
        return (defecto,
                "Circle what you choose and cross out what you leave: choosing one thing means leaving "
                "another. Then write how much money you have left.",
                "I have \\huecoRespuesta\\ euros left",
                "any answer is fine: " + "; ".join(f"{self.el(o)}, {self.sobra(tengo - p)}" for o, p in cosas))

    def compara(self, barata, cara):
        return ("Look at the price in both shops. Circle the shop where it is cheaper, and write how "
                "much you save: the difference between the two prices.",
                "I save \\huecoRespuesta\\ euros",
                f"“{barata[0]}”, €{barata[1]} and not €{cara[1]}: you save €{cara[1] - barata[1]}")

    def cuentas(self, quedas):
        return ("How much is left after each line?",
                "Start with what there is at the beginning. If money comes in, add it; if it goes "
                "out, take it away. Write what is left in each box.",
                "left: " + ", ".join(f"€{q}" for q in quedas) + f"; at the end, €{quedas[-1]}")


ESPANOL = Espanol()
INGLES = Ingles()
