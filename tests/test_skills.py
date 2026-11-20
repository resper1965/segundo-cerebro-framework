import re

import pytest

from conftest import gerar

SKILLS = ["implantar-cerebro", "curar-hot", "triagem-inbox", "revisao-semanal", "promover-memoria", "rotear-fontes", "perguntas-ouro"]


def _frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    assert m, "sem frontmatter"
    return dict(linha.split(": ", 1) for linha in m.group(1).splitlines() if ": " in linha)


@pytest.fixture(scope="module")
def cerebro(tmp_path_factory):
    return gerar(tmp_path_factory.mktemp("s") / "c")


@pytest.mark.parametrize("nome", SKILLS)
def test_skill_tem_nome_e_descricao(cerebro, nome):
    fm = _frontmatter((cerebro / "_system" / "skills" / nome / "SKILL.md").read_text(encoding="utf-8"))
    assert fm["name"] == nome
    assert 20 <= len(fm["description"]) <= 1024


def test_implantar_cerebro_tem_regras_criticas(cerebro):
    texto = (cerebro / "_system" / "skills" / "implantar-cerebro" / "SKILL.md").read_text(encoding="utf-8")
    for termo in ["gate", "wrangler", "_implantacao/status.md", "_maps/decisoes.md", "nunca pula"]:
        assert termo in texto.lower() or termo in texto, termo


def test_aplicar_marca_so_com_design_system(tmp_path, cerebro):
    assert not (cerebro / "_system" / "skills" / "aplicar-marca").exists()
    com = gerar(tmp_path / "ds", modulos=["design-system"])
    assert (com / "_system" / "skills" / "aplicar-marca" / "SKILL.md").exists()


def test_implantar_cerebro_reconcilia_e_segue_ordem(cerebro):
    texto = (cerebro / "_system" / "skills" / "implantar-cerebro" / "SKILL.md").read_text(encoding="utf-8")
    assert "## Reconciliar (sempre antes de `status` e `proxima`)" in texto
    assert "como `pendente`" in texto and "_maps/fontes.md" in texto and "pergunte ao consultor" in texto
    assert "cujas dependências" not in texto
    assert "a próxima etapa pendente na ordem do roteiro; só avance de fase quando todas as etapas da fase anterior " \
           "estiverem `feita` e o gate de fase (se houver) aprovado" in texto
    assert "--estrito" in texto


def test_curar_hot_estrito_e_triagem_arquiva(cerebro):
    skills = cerebro / "_system" / "skills"
    assert "brain_check.py . --estrito" in (skills / "curar-hot" / "SKILL.md").read_text(encoding="utf-8")
    triagem = (skills / "triagem-inbox" / "SKILL.md").read_text(encoding="utf-8")
    assert "`04-arquivo/`" in triagem and "nunca apague" in triagem and "confirme antes de apagar" not in triagem
