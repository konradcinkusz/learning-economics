"""Negative fixtures for tools/checklog.py (synthetic LaTeX logs)."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools" / "checklog.py"


def run(tmp_path, texto):
    log = tmp_path / "t.log"
    log.write_text(texto, encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), str(log)],
                          capture_output=True, text=True)


def test_clean_log_passes(tmp_path):
    r = run(tmp_path, "This is LuaTeX\nOutput written on t.pdf (3 pages)\n")
    assert r.returncode == 0 and "OK" in r.stdout


def test_file_line_error_is_caught(tmp_path):
    # With -file-line-error the line starts with a path, not "!".
    r = run(tmp_path, "./t.tex:42: Undefined control sequence.\nl.42 \\foo\n")
    assert r.returncode == 1
    assert "t.tex:42" in r.stderr


def test_overfull_box_fails(tmp_path):
    r = run(tmp_path, "Overfull \\hbox (3.2pt too wide) in paragraph at lines 1--2\n")
    assert r.returncode == 1 and "OVERFULL" in r.stderr
    r = run(tmp_path, "Overfull \\vbox (1.0pt too high) has occurred\n")
    assert r.returncode == 1


def test_missing_glyph_fails(tmp_path):
    r = run(tmp_path, "Missing character: There is no \u2605 in font Andika!\n")
    assert r.returncode == 1


def test_fatal_error_fails(tmp_path):
    r = run(tmp_path, "Fatal error occurred, no output PDF file produced!\n")
    assert r.returncode == 1


def test_underfull_is_not_blocking(tmp_path):
    r = run(tmp_path, "Underfull \\hbox (badness 10000) in paragraph\n")
    assert r.returncode == 0 and "underfull" in r.stdout


def test_missing_file_fails(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path / "nope.log")],
                       capture_output=True, text=True)
    assert r.returncode == 1


def test_no_arguments_is_usage_error():
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert r.returncode == 2
