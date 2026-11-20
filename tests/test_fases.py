from pathlib import Path

import yaml

from conftest import KIT, gerar


def test_nucleo_tem_seis_fases_com_ids_unicos():
    fases = yaml.safe_load((KIT / "fases" / "nucleo.yml").read_text(encoding="utf-8"))
    assert [f["numero"] for f in fases] == [0, 1, 2, 3, 4, 5]
    ids = [e["id"] for f in fases for e in f["etapas"]]
    assert len(ids) == len(set(ids))
    for f in fases:
        for e in f["etapas"]:
            assert e["id"].startswith(f"F{f['numero']}.")
            assert e["quem"] in {"consultor", "cliente", "agente"}
            assert {"titulo", "gate", "saida", "pronto_quando"} <= set(e)


def test_roteiro_e_status_gerados(tmp_path):
    c = gerar(tmp_path / "c")
    roteiro = (c / "_implantacao" / "roteiro.md").read_text(encoding="utf-8")
    status = (c / "_implantacao" / "status.md").read_text(encoding="utf-8")
    assert "## F0 — Preparação" in roteiro
    assert "## F5 — Entrega" in roteiro
    assert "F3.5" in roteiro
    assert "| F0.1 |" in status and "| pendente |" in status
    ouro = (c / "_implantacao" / "perguntas-ouro.md").read_text(encoding="utf-8")
    assert ouro.count("\n## Pergunta ") == 10


def test_index_linka_implantacao(tmp_path):
    index = (gerar(tmp_path / "c") / "_maps" / "index.md").read_text(encoding="utf-8")
    assert "[[_implantacao/roteiro]]" in index
