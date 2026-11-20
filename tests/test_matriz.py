import importlib.util
from datetime import date

import pytest

from conftest import KIT, gerar
from modulos_lib import carregar_modulos

TODOS = sorted(carregar_modulos(KIT / "modulos"))


def _bc(c):
    spec = importlib.util.spec_from_file_location("bc", c / "_system" / "ferramentas" / "brain_check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("vertical", ["pessoal", "empresa", "juridico"])
def test_verticais_verdes(tmp_path, vertical):
    c = gerar(tmp_path / vertical, vertical=vertical, modulos=None)
    assert _bc(c).verificar(c, date.today()) == []


def test_todos_os_modulos_juntos_verdes(tmp_path):
    c = gerar(tmp_path / "todos", modulos=TODOS)
    assert _bc(c).verificar(c, date.today()) == []
    status = (c / "_implantacao" / "status.md").read_text(encoding="utf-8")
    assert "| M-teses.2 |" in status and "| M-propostas.1 |" in status
    assert len(TODOS) == 18
