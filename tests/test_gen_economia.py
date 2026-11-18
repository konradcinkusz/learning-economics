"""Negative and positive tests for the validators in tools/gen_economia.py.

All fixtures are synthetic: a ten-day, two-week notebook built here, using
the real week themes from tools/idiomas.py. No book content is read.
"""
import copy

import pytest

import gen_economia as g
from idiomas import ESPANOL


def _semanas():
    return {
        1: {"semana": 1, "palabra": "valor", "definicion": "Lo que vale algo.",
            "formas": ["valor", "vale"]},
        2: {"semana": 2, "palabra": "trueque", "definicion": "Cambiar una cosa por otra.",
            "formas": ["trueque", "truecan"]},
    }


def _dias():
    dias = []
    for n in range(1, 11):
        semana = (n - 1) // 5 + 1
        viernes = n % 5 == 0
        palabra = "valor" if semana == 1 else "trueque"
        dias.append({
            "dia": n, "semana": semana, "tema": ESPANOL.temas[semana - 1],
            "objeto": "lupa",
            # Mondays say the word of the week.
            "historia": f"Hoy se habla de {palabra}." if n % 5 == 1 else "Una historia corta.",
            "actividad": ({"tipo": "repasa", "checklist": ["a"], "prompt": "p"} if viernes
                          else {"tipo": "dibuja", "prompt": "Dibuja."}),
        })
    return dias


def validar(dias, semanas):
    g.validar_dias(dias, semanas, ESPANOL, escritos=10)


def test_valid_fixture_passes():
    validar(_dias(), _semanas())


def test_missing_day_is_rejected():
    dias = _dias()
    del dias[3]
    with pytest.raises(g.ErrorDeContenido, match="sin huecos"):
        validar(dias, _semanas())


def test_wrong_week_number_is_rejected():
    dias = _dias()
    dias[0]["semana"] = 2
    with pytest.raises(g.ErrorDeContenido, match="es de la semana 1"):
        validar(dias, _semanas())


def test_wrong_theme_is_rejected():
    dias = _dias()
    dias[1]["tema"] = "otro tema"
    with pytest.raises(g.ErrorDeContenido, match="el tema de la semana 1"):
        validar(dias, _semanas())


def test_unknown_object_is_rejected():
    dias = _dias()
    dias[1]["objeto"] = "no-existe"
    with pytest.raises(g.ErrorDeContenido, match="no hay dibujo"):
        validar(dias, _semanas())


def test_story_over_word_limit_is_rejected():
    dias = _dias()
    dias[1]["historia"] = " ".join(["palabra"] * (g.MAX_PALABRAS_HISTORIA + 1))
    with pytest.raises(g.ErrorDeContenido, match="palabras"):
        validar(dias, _semanas())


def test_monday_must_say_the_word_of_the_week():
    dias = _dias()
    dias[0]["historia"] = "Una historia sin la palabra."
    with pytest.raises(g.ErrorDeContenido, match="lunes"):
        validar(dias, _semanas())


def test_friday_must_be_review_and_only_friday():
    dias = _dias()
    dias[4]["actividad"] = {"tipo": "dibuja", "prompt": "x"}
    with pytest.raises(g.ErrorDeContenido, match="repasa"):
        validar(dias, _semanas())
    dias = _dias()
    dias[1]["actividad"] = {"tipo": "repasa", "checklist": ["a"], "prompt": "p"}
    with pytest.raises(g.ErrorDeContenido, match="repasa"):
        validar(dias, _semanas())


def test_missing_field_is_rejected():
    dias = _dias()
    del dias[2]["historia"]
    with pytest.raises(g.ErrorDeContenido, match="falta 'historia'"):
        validar(dias, _semanas())


def test_validar_semanas_negative_cases():
    ok = _semanas()
    g.validar_semanas(ok, 2)
    with pytest.raises(g.ErrorDeContenido, match="sin huecos"):
        g.validar_semanas({1: ok[1]}, 2)
    s = copy.deepcopy(ok)
    s[2]["palabra"] = "valor"
    s[2]["formas"] = ["valor"]
    with pytest.raises(g.ErrorDeContenido, match="ya es la de la semana"):
        g.validar_semanas(s, 2)
    s = copy.deepcopy(ok)
    s[1]["palabra"] = "Valor"
    with pytest.raises(g.ErrorDeContenido, match="minúsculas"):
        g.validar_semanas(s, 2)
    s = copy.deepcopy(ok)
    s[1]["formas"] = ["vale"]
    with pytest.raises(g.ErrorDeContenido, match="entre sus formas"):
        g.validar_semanas(s, 2)
    s = copy.deepcopy(ok)
    s[1]["definicion"] = "sin mayúscula ni punto"
    with pytest.raises(g.ErrorDeContenido, match="definición"):
        g.validar_semanas(s, 2)
    s = copy.deepcopy(ok)
    del s[1]["definicion"]
    with pytest.raises(g.ErrorDeContenido, match="falta 'definicion'"):
        g.validar_semanas(s, 2)


def test_money_ladder_per_quarter():
    # Quarter 1 (week 1): max 20 EUR, notes 5/10/20 only.
    g.comprobar_dinero(1, 1, [10, 5, 2], "x")
    with pytest.raises(g.ErrorDeContenido):
        g.comprobar_dinero(1, 1, [20, 5], "x")        # 25 > 20
    with pytest.raises(g.ErrorDeContenido):
        g.comprobar_dinero(1, 1, [50], "x")           # 50 note not yet available
    with pytest.raises(g.ErrorDeContenido):
        g.comprobar_dinero(1, 1, [3], "x")            # no 3 EUR coin
    with pytest.raises(g.ErrorDeContenido):
        g.comprobar_dinero(1, 1, [], "x")
    g.comprobar_dinero(1, 14, [50], "x")              # quarter 2 allows it


def test_quantity_limits():
    g.comprobar_cantidad(1, 1, 20, "x")
    for bad in (21, -1, "5", 2.5):
        with pytest.raises(g.ErrorDeContenido):
            g.comprobar_cantidad(1, 1, bad, "x")


def test_escapar_latex_specials_and_nbsp_euro():
    assert g.escapar("5 € & 10% #1 _x") == r"5~€ \& 10\% \#1 \_x"


def test_dice_matches_whole_words_only():
    assert g.dice("El precio sube.", ["precio"])
    assert not g.dice("Los precios suben.", ["precio"])
