import importlib.util
import sys
from datetime import date

import pytest

from conftest import KIT, gerar
from modulos_lib import carregar_modulos, validar_modulos

MODULOS = carregar_modulos(KIT / "modulos")

sys.path.insert(0, str(KIT / "tools"))
from novo_modulo import criar_stubs  # noqa: E402


def _brain_check(cerebro):
    spec = importlib.util.spec_from_file_location("bc", cerebro / "_system" / "ferramentas" / "brain_check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_contrato_de_todos_os_modulos():
    assert validar_modulos(MODULOS, kit=KIT) == []


@pytest.mark.parametrize("mid", sorted(MODULOS))
def test_modulo_isolado_gera_e_fica_verde(tmp_path, mid):
    c = gerar(tmp_path / mid, modulos=[mid])
    m = MODULOS[mid]
    assert (c / m["pasta"] / "README.md").exists()
    assert (c / "_maps" / f"mapa-{mid}.md").exists()
    assert (c / "_system" / "templates" / f"{m['template']}.md").exists()
    assert f"[[_maps/mapa-{mid}]]" in (c / "_maps" / "index.md").read_text(encoding="utf-8")
    assert f"`{m['pasta']}/`" in (c / "RESOLVER.md").read_text(encoding="utf-8")
    assert _brain_check(c).verificar(c, date.today()) == []


def test_modulo_inativo_nao_aparece(tmp_path):
    c = gerar(tmp_path / "c", modulos=[])
    assert not any(p.name[:2].isdigit() and int(p.name[:2]) >= 6 for p in c.iterdir())


def test_criar_stubs_nao_sobrescreve(tmp_path):
    kit = tmp_path / "kit"
    (kit / "modulos" / "xpto").mkdir(parents=True)
    (kit / "modulos" / "xpto" / "modulo.yml").write_text("id: xpto\npasta: 99-xpto\n", encoding="utf-8")
    criados = criar_stubs("xpto", kit)
    assert len(criados) == 2 and all(p.exists() for p in criados)
    criados[0].write_text("editado", encoding="utf-8")
    criar_stubs("xpto", kit)
    assert criados[0].read_text(encoding="utf-8") == "editado"
