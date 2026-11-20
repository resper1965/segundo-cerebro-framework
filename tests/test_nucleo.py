from datetime import date

from conftest import gerar

PASTAS = ["00-inbox", "01-projetos", "02-areas", "03-recursos", "04-arquivo", "05-pessoas", "diario"]
MAPAS = ["hot", "index", "fontes", "decisoes", "glossario", "mapa-projetos", "mapa-areas", "mapa-pessoas", "mapa-recursos"]
TEMPLATES = ["projeto", "area", "recurso", "pessoa", "decisao", "diario", "revisao-semanal"]


def test_estrutura_para_e_mapas(tmp_path):
    c = gerar(tmp_path / "c")
    for p in PASTAS:
        assert (c / p / "README.md").exists(), p
    for m in MAPAS:
        assert (c / "_maps" / f"{m}.md").exists(), m
    for t in TEMPLATES:
        assert (c / "_system" / "templates" / f"template-{t}.md").exists(), t
    for f in ["CLAUDE.md", "AGENTS.md", "RESOLVER.md", "_system/AGENTS.md", "_system/convencoes.md"]:
        assert (c / f).exists(), f


def test_hot_tem_frontmatter_e_data_de_hoje(tmp_path):
    hot = (gerar(tmp_path / "c") / "_maps" / "hot.md").read_text(encoding="utf-8")
    assert hot.startswith("---\ntype: mapa\n")
    assert f"updated: {date.today().isoformat()}" in hot
    assert "Cliente Teste" in hot


def test_templates_mantem_placeholders_do_obsidian(tmp_path):
    pessoa = (gerar(tmp_path / "c") / "_system" / "templates" / "template-pessoa.md").read_text(encoding="utf-8")
    assert "created: {{date}}" in pessoa
    assert "bio_publicavel: false" in pessoa
    assert "### Curta (~50 palavras)" in pessoa
    assert "## Linha do tempo" in pessoa


def test_links_do_index_tem_caminho(tmp_path):
    index = (gerar(tmp_path / "c") / "_maps" / "index.md").read_text(encoding="utf-8")
    assert "[[_maps/hot]]" in index
    assert "[[_system/AGENTS]]" in index


def test_claude_md_aponta_para_agents(tmp_path):
    assert "@_system/AGENTS.md" in (gerar(tmp_path / "c") / "CLAUDE.md").read_text(encoding="utf-8")
