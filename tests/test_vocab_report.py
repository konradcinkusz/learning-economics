import vocab_report as v


def _dias(historias):
    return [{"dia": i + 1, "historia": h, "actividad": {"tipo": "dibuja", "prompt": p}}
            for i, (h, p) in enumerate(historias)]


SEMANAS = {1: {"palabra": "valor", "formas": ["valor", "vale"]},
           2: {"palabra": "trueque", "formas": ["trueque"]}}


def test_word_used_in_story_before_its_week_is_reported():
    dias = _dias([("Hola", "x")] * 5 + [("Hola", "x")] * 5)
    dias[2]["historia"] = "Hacen un trueque."
    hits = v.informe(dias, SEMANAS)
    assert [(h[1], h[3], h[4]) for h in hits] == [("trueque", 3, "historia")]


def test_activity_text_counts_and_only_first_use_is_reported():
    dias = _dias([("Hola", "x")] * 10)
    dias[1]["actividad"]["prompt"] = "El trueque"
    dias[3]["historia"] = "otro trueque"
    hits = v.informe(dias, SEMANAS)
    assert len(hits) == 1 and hits[0][3] == 2 and hits[0][4] == "actividad.prompt"


def test_use_in_own_week_is_not_reported():
    dias = _dias([("Hola", "x")] * 10)
    dias[5]["historia"] = "Un trueque."
    assert v.informe(dias, SEMANAS) == []


def test_json_keys_are_not_text():
    dias = _dias([("Hola", "x")] * 10)
    dias[0]["actividad"] = {"tipo": "dibuja", "trueque": 3}
    assert v.informe(dias, SEMANAS) == []
