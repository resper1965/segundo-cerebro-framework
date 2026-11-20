import importlib.util
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

from conftest import gerar


def _carregar(cerebro: Path):
    spec = importlib.util.spec_from_file_location("brain_check", cerebro / "_system" / "ferramentas" / "brain_check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cerebro_recem_gerado_esta_verde(tmp_path):
    c = gerar(tmp_path / "c")
    assert _carregar(c).verificar(c, date.today()) == []


def test_detecta_problemas(tmp_path):
    c = gerar(tmp_path / "c")
    bc = _carregar(c)
    (c / "01-projetos" / "sem-fm.md").write_text("# x\n", encoding="utf-8")
    (c / "01-projetos" / "sem-tipo.md").write_text("---\ncreated: 2026-01-01\n---\n# y\n", encoding="utf-8")
    (c / "01-projetos" / "links.md").write_text(
        "---\ntype: projeto\ncreated: 2026-01-01\n---\n[[curto]] [[01-projetos/nao-existe]] `[[ignorado]]` {{x}}\n",
        encoding="utf-8",
    )
    erros = "\n".join(bc.verificar(c, date.today()))
    assert "01-projetos/sem-fm.md: sem frontmatter" in erros
    assert "01-projetos/sem-tipo.md: frontmatter sem 'type'" in erros
    assert "01-projetos/links.md: link sem caminho [[curto]]" in erros
    assert "01-projetos/links.md: link quebrado [[01-projetos/nao-existe]]" in erros
    assert "ignorado" not in erros
    assert "01-projetos/links.md: placeholder não resolvido" in erros


def test_hot_vencido_e_longo(tmp_path):
    c = gerar(tmp_path / "c")
    bc = _carregar(c)
    assert any("vencido" in e for e in bc.verificar(c, date.today() + timedelta(days=8)))
    hot = c / "_maps" / "hot.md"
    hot.write_text(hot.read_text(encoding="utf-8") + "\n".join(f"- item {i}" for i in range(40)), encoding="utf-8")
    assert any("máx. 40" in e for e in bc.verificar(c, date.today()))


def test_cli_retorna_codigo(tmp_path):
    c = gerar(tmp_path / "c")
    script = c / "_system" / "ferramentas" / "brain_check.py"
    assert subprocess.run([sys.executable, str(script), str(c)]).returncode == 0
    (c / "01-projetos" / "ruim.md").write_text("# sem frontmatter\n", encoding="utf-8")
    assert subprocess.run([sys.executable, str(script), str(c)], capture_output=True).returncode == 1


def test_precommit_tem_gitleaks_e_brain_check(tmp_path):
    cfg = yaml.safe_load((gerar(tmp_path / "c") / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    ids = [h["id"] for r in cfg["repos"] for h in r["hooks"]]
    assert "gitleaks" in ids and "brain-check" in ids


def test_preset_obsidian_opcional(tmp_path):
    com = gerar(tmp_path / "com")
    app = json.loads((com / ".obsidian" / "app.json").read_text(encoding="utf-8"))
    assert app["newLinkFormat"] == "absolute"
    assert not (gerar(tmp_path / "sem", obsidian=False) / ".obsidian").exists()
