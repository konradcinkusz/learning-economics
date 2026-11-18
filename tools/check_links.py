#!/usr/bin/env python3
"""Check that the PDF links in docs/index.html and README.md point at
files that .github/workflows/pages.yml really publishes.

pages.yml copies each build into _site under a public name
(`cp polish-bw.pdf _site/poznaje-ekonomie-cz-b.pdf`). A link to any other
name is a 404 on the live site. Read-only; standard library only.

Checked:
  - docs/index.html: every relative href ending in .pdf;
  - README.md: every link to <pages-url>/<name>.pdf of this repository.
Also reported (not a failure): published PDFs that neither file links to.

Usage:
    python3 tools/check_links.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_URL = "https://konradcinkusz.github.io/learning-economics/"

PATRON_CP = re.compile(r"^\s*cp\s+\S+\.pdf\s+_site/(\S+\.pdf)\s*$", re.MULTILINE)
PATRON_HREF = re.compile(r"""href\s*=\s*["']([^"']+\.pdf)["']""")
PATRON_MD = re.compile(r"\]\((" + re.escape(PAGES_URL) + r"[^)\s]+\.pdf)\)")


def publicados(texto_pages):
    return set(PATRON_CP.findall(texto_pages))


def enlaces_html(texto):
    return [h for h in PATRON_HREF.findall(texto) if "://" not in h]


def enlaces_readme(texto):
    return [u[len(PAGES_URL):] for u in PATRON_MD.findall(texto)]


def revisar(pages, html, readme):
    """Return (problems, unlinked)."""
    pub = publicados(pages)
    problemas = []
    if not pub:
        problemas.append("pages.yml no copia ningún PDF a _site/")
    usados = set()
    for origen, enlaces in (("docs/index.html", enlaces_html(html)),
                            ("README.md", enlaces_readme(readme))):
        if not enlaces:
            problemas.append(f"{origen}: no se encontró ningún enlace a un PDF")
        for e in enlaces:
            usados.add(e)
            if e not in pub:
                problemas.append(f"{origen}: enlaza {e}, que pages.yml no publica")
    return problemas, sorted(pub - usados)


def main():
    leer = lambda r: (ROOT / r).read_text(encoding="utf-8")
    problemas, sin_enlace = revisar(leer(".github/workflows/pages.yml"),
                                    leer("docs/index.html"), leer("README.md"))
    for s in sin_enlace:
        print(f"aviso: pages.yml publica {s} pero nadie lo enlaza")
    if problemas:
        for p in problemas:
            print(f"ERROR: {p}", file=sys.stderr)
        return 1
    print("OK: todos los enlaces a PDF de docs/index.html y README.md se publican en pages.yml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
