#!/usr/bin/env python3
"""WARNING-level report: weekly-vocabulary words used before their week.

Each week of content/q*.json has a word of the week (`semanas[].palabra`)
with the forms it can take (`formas`). The word is introduced on the Monday
of its week. This script lists the words whose forms already appear, as
whole words, in the story or activity text of an EARLIER day.

Read-only and informational: it never changes content or lesson order and
always exits 0. Matching is by exact surface form, so each hit needs a
human read: a form can be an ordinary word in another sense (e.g. "vale"
as the verb "to be worth" vs. "vale" as a voucher), which is a
false positive for the teaching order. Whether to move a lesson or gloss a
word is a pedagogical decision for the book's owner.

Usage:
    python3 tools/vocab_report.py [--context]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gen_economia as g  # noqa: E402


def textos(dia):
    """(where, text) pairs of a day: the story, then every string in the
    activity (prompts, questions, cards, steps...)."""
    yield "historia", dia["historia"]

    def recorre(valor, ruta):
        if isinstance(valor, str):
            yield ruta, valor
        elif isinstance(valor, dict):
            for k, v in valor.items():
                yield from recorre(v, f"{ruta}.{k}")
        elif isinstance(valor, list):
            for i, v in enumerate(valor):
                yield from recorre(v, f"{ruta}[{i}]")

    yield from recorre(dia["actividad"], "actividad")


def informe(dias, semanas):
    """Return a list of hits: (week, word, intro_day, first_day, where,
    text), one per word that is used early, ordered by week."""
    hallazgos = []
    for n, s in sorted(semanas.items()):
        intro = (n - 1) * g.DIAS_POR_SEMANA + 1
        hecho = False
        for d in dias:
            if d["dia"] >= intro or hecho:
                break
            for donde, texto in textos(d):
                if g.dice(texto, s["formas"]):
                    hallazgos.append((n, s["palabra"], intro, d["dia"], donde, texto))
                    hecho = True
                    break
    return hallazgos


def main():
    con_contexto = "--context" in sys.argv
    dias, semanas = g.cargar()
    hallazgos = informe(dias, semanas)
    for n, palabra, intro, dia, donde, texto in hallazgos:
        print(f"AVISO: «{palabra}» (semana {n}, día {intro}) ya se usa en el día {dia} ({donde})")
        if con_contexto:
            print(f"       {texto}")
    print(f"{len(hallazgos)} palabra(s) de {len(semanas)} usadas antes de su semana "
          "(solo informativo: revisar a mano; no falla).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
