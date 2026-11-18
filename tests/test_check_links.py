import check_links as c

PAGES = """
      - run: |
          cp main.pdf _site/a.pdf
          cp polish-bw.pdf _site/p-bw.pdf
"""
URL = c.PAGES_URL


def test_real_repo_links_are_consistent():
    assert c.main() == 0


def test_ok():
    problemas, sin = c.revisar(PAGES, '<a href="a.pdf">x</a><a href="p-bw.pdf">y</a>',
                               f"[a]({URL}a.pdf) [b]({URL}p-bw.pdf)")
    assert problemas == [] and sin == []


def test_dangling_html_href():
    problemas, _ = c.revisar(PAGES, '<a href="polish-bw.pdf">y</a><a href="a.pdf">x</a>',
                             f"[a]({URL}a.pdf)")
    assert any("docs/index.html" in p and "polish-bw.pdf" in p for p in problemas)


def test_dangling_readme_link():
    problemas, _ = c.revisar(PAGES, '<a href="a.pdf">x</a>', f"[a]({URL}zzz.pdf)")
    assert any("README.md" in p and "zzz.pdf" in p for p in problemas)


def test_external_html_links_ignored_and_unlinked_reported():
    problemas, sin = c.revisar(PAGES, '<a href="https://x.org/q.pdf">q</a><a href="a.pdf">x</a>',
                               f"[a]({URL}a.pdf)")
    assert problemas == [] and sin == ["p-bw.pdf"]


def test_no_published_pdfs_is_a_problem():
    problemas, _ = c.revisar("nothing", '<a href="a.pdf">x</a>', f"[a]({URL}a.pdf)")
    assert problemas


def test_main_exit_code_is_the_ci_gate(tmp_path, monkeypatch):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / ".github" / "workflows" / "pages.yml").write_text(PAGES, encoding="utf-8")
    (tmp_path / "README.md").write_text(f"[a]({URL}a.pdf)", encoding="utf-8")
    (tmp_path / "docs" / "index.html").write_text('<a href="a.pdf">x</a>', encoding="utf-8")
    monkeypatch.setattr(c, "ROOT", tmp_path)
    assert c.main() == 0
    (tmp_path / "docs" / "index.html").write_text('<a href="gone.pdf">x</a>', encoding="utf-8")
    assert c.main() == 1
