from pathlib import Path

import pytest
import yaml

from modulos_lib import carregar_fases, carregar_modulos, resolver_dependencias, validar_modulos


def _modulo(pasta_modulos: Path, mid: str, **campos) -> None:
    base = {
        "id": mid, "nome": mid.title(), "descricao": "d", "depende_de": [], "pasta": f"90-{mid}",
        "entra": "e", "nao_entra": "n", "mapa": {"titulo": mid, "colunas": ["A", "B"]},
        "template": f"template-{mid}", "implantacao": [], "sistema": {"modo": "canonico"}, "agentes": [],
    }
    base.update(campos)
    (pasta_modulos / mid).mkdir(parents=True)
    (pasta_modulos / mid / "modulo.yml").write_text(yaml.safe_dump(base, allow_unicode=True), encoding="utf-8")


def test_carregar_modulos_indexa_por_id(tmp_path):
    _modulo(tmp_path, "casos")
    assert list(carregar_modulos(tmp_path)) == ["casos"]


def test_carregar_modulos_pasta_vazia(tmp_path):
    assert carregar_modulos(tmp_path) == {}


def test_resolver_inclui_dependencias_transitivas_e_ordena_por_pasta(tmp_path):
    _modulo(tmp_path, "clientes", pasta="06-clientes")
    _modulo(tmp_path, "casos", pasta="11-casos", depende_de=["clientes"])
    _modulo(tmp_path, "teses", pasta="12-teses", depende_de=["casos"])
    mods = carregar_modulos(tmp_path)
    assert resolver_dependencias(["teses"], mods) == ["clientes", "casos", "teses"]


def test_resolver_rejeita_modulo_desconhecido(tmp_path):
    with pytest.raises(ValueError, match="módulo desconhecido: xpto"):
        resolver_dependencias(["xpto"], {})


def test_validar_aceita_modulo_correto(tmp_path):
    _modulo(tmp_path, "casos", pasta="11-casos")
    assert validar_modulos(carregar_modulos(tmp_path)) == []


def test_validar_aponta_erros(tmp_path):
    _modulo(tmp_path, "a", pasta="11-x", depende_de=["fantasma"], sistema={"modo": "outro"},
            implantacao=[{"id": "F9.1", "fase": 9, "titulo": "t", "quem": "robo", "gate": False}])
    _modulo(tmp_path, "b", pasta="11-x", template="tpl-b")
    erros = "\n".join(validar_modulos(carregar_modulos(tmp_path)))
    assert "a: depende de módulo inexistente 'fantasma'" in erros
    assert "a: sistema.modo inválido 'outro'" in erros
    assert "a: etapa 'F9.1' deve começar com 'M-a.'" in erros
    assert "a: etapa 'F9.1' com fase inválida 9" in erros
    assert "a: etapa 'F9.1' com quem inválido 'robo'" in erros
    assert "pasta '11-x' repetida" in erros
    assert "b: template deve começar com 'template-'" in erros


def test_validar_campo_obrigatorio(tmp_path):
    (tmp_path / "z").mkdir()
    (tmp_path / "z" / "modulo.yml").write_text("id: z\n", encoding="utf-8")
    assert "z: campo obrigatório ausente 'nome'" in validar_modulos(carregar_modulos(tmp_path))


def test_carregar_fases_mescla_etapas_de_modulo(tmp_path):
    arq = tmp_path / "nucleo.yml"
    arq.write_text(
        "- numero: 2\n  nome: Estrutura\n  objetivo: o\n  pronto_quando: p\n  gate: true\n"
        "  etapas:\n    - {id: F2.1, titulo: t, quem: consultor, gate: false}\n",
        encoding="utf-8",
    )
    mods = [{"id": "teses", "implantacao": [{"id": "M-teses.1", "fase": 2, "titulo": "x", "quem": "agente", "gate": True}]}]
    fases = carregar_fases(arq, mods)
    assert [e["id"] for e in fases[0]["etapas"]] == ["F2.1", "M-teses.1"]
