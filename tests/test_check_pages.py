"""Negative fixtures for tools/check_pages.py (synthetic .aux files)."""
import re
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools" / "check_pages.py"


def aux(overrides=None, drop=(), clave_extra=1, days=260):
    """A valid .aux: day 1 on page 5, one page per day, a medal page after
    days 65/130/195, and the answer key right after the last day."""
    saltos = {65: 2, 130: 2, 195: 2}
    paginas, p = {}, 5
    for d in range(1, days + 1):
        paginas[d] = p
        p += saltos.get(d, 1)
    paginas.update(overrides or {})
    lineas = [f"\\newlabel{{dia:{d}}}{{{{{d}}}{{{pg}}}}}" for d, pg in paginas.items()
              if d not in drop]
    lineas.append(f"\\newlabel{{clave}}{{{{1}}{{{paginas[days] + clave_extra}}}}}")
    return "\n".join(lineas) + "\n"


def run(tmp_path, texto):
    f = tmp_path / "t.aux"
    f.write_text(texto, encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), str(f)], capture_output=True, text=True)


def test_valid_aux_passes(tmp_path):
    r = run(tmp_path, aux())
    assert r.returncode == 0, r.stderr
    assert "260 días" in r.stdout


def test_overflowing_day_is_reported_with_its_number(tmp_path):
    # Day 100 spills onto a second page: every later day shifts by one.
    base = {}
    for line in aux().splitlines():
        m = re.match(r"\\newlabel\{dia:(\d+)\}\{\{\d+\}\{(\d+)\}", line)
        if m:
            base[int(m.group(1))] = int(m.group(2))
    shifted = {d: base[d] + 1 for d in range(101, 261)}
    r = run(tmp_path, aux(overrides=shifted))
    assert r.returncode == 1
    assert "día 100" in r.stderr


def test_missing_day_is_reported(tmp_path):
    r = run(tmp_path, aux(drop={50}))
    assert r.returncode == 1 and "falta el día 50" in r.stderr


def test_day_one_on_wrong_page(tmp_path):
    texto = aux()
    texto = texto.replace("\\newlabel{dia:1}{{1}{5}", "\\newlabel{dia:1}{{1}{6}")
    r = run(tmp_path, texto)
    assert r.returncode == 1 and "el día 1 está en la página 6" in r.stderr


def test_last_day_overflow_before_answer_key(tmp_path):
    r = run(tmp_path, aux(clave_extra=2))
    assert r.returncode == 1 and "clave de respuestas" in r.stderr


def test_aux_without_day_labels_fails(tmp_path):
    r = run(tmp_path, "\\relax\n")
    assert r.returncode == 1 and "ninguna etiqueta" in r.stderr


def test_missing_aux_fails(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path / "nope.aux")],
                       capture_output=True, text=True)
    assert r.returncode == 1
