import json

from conftest import gerar


def test_design_system_traz_tokens_e_regras(tmp_path):
    c = gerar(tmp_path / "c", modulos=["design-system"])
    tokens = json.loads((c / "17-design-system" / "tokens.json").read_text(encoding="utf-8"))
    assert "color" in tokens and "$type" in tokens["color"]["primaria"]
    assert (c / "17-design-system" / "design.md").exists()
    assert (c / "17-design-system" / "voz-e-tom.md").exists()


def test_propostas_puxa_ofertas_e_tem_equipe(tmp_path):
    c = gerar(tmp_path / "c", modulos=["propostas"])
    assert (c / "21-ofertas").is_dir()
    tpl = (c / "_system" / "templates" / "template-proposta.md").read_text(encoding="utf-8")
    assert "equipe: []" in tpl and "oferta:" in tpl


def test_ofertas_sem_preco(tmp_path):
    c = gerar(tmp_path / "c", modulos=["ofertas"])
    tpl = (c / "_system" / "templates" / "template-oferta.md").read_text(encoding="utf-8").lower()
    assert "preço" in tpl and "área comercial" in tpl
    assert "valor:" not in tpl and "preco:" not in tpl


def test_onboarding_comece_aqui(tmp_path):
    c = gerar(tmp_path / "c", modulos=["onboarding"])
    assert "[[_maps/index]]" in (c / "19-onboarding" / "comece-aqui.md").read_text(encoding="utf-8")
