import shutil
import subprocess

import copier
import yaml

from conftest import KIT


def _git(pasta, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=pasta, check=True, capture_output=True)


def test_update_preserva_conteudo_do_cliente(tmp_path):
    kit = tmp_path / "kit"
    shutil.copytree(KIT, kit, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".superpowers"))
    _git(kit, "init", "-q")
    _git(kit, "add", "-A")
    _git(kit, "commit", "-qm", "v1")
    _git(kit, "tag", "v0.1.0")

    cerebro = tmp_path / "cerebro"
    copier.run_copy(str(kit), str(cerebro), data={"nome": "Cliente", "vertical": "empresa", "responsavel": "C"},
                    defaults=True, unsafe=True, quiet=True, vcs_ref="v0.1.0")
    hot_cliente = "---\ntype: mapa\ncreated: 2026-01-01\nupdated: 2026-01-01\n---\n# Hot do cliente\n- foco real\n"
    (cerebro / "_maps" / "hot.md").write_text(hot_cliente, encoding="utf-8")
    nota = cerebro / "06-clientes" / "acme.md"
    nota.write_text("---\ntype: cliente\ncreated: 2026-01-01\n---\n# Acme\n", encoding="utf-8")
    mapa = cerebro / "_maps" / "mapa-clientes.md"
    mapa.write_text(mapa.read_text(encoding="utf-8") + "| [[06-clientes/acme]] | ativo | Ana | renovar |\n", encoding="utf-8")
    _git(cerebro, "init", "-q")
    _git(cerebro, "add", "-A")
    _git(cerebro, "commit", "-qm", "conteúdo do cliente")

    agents = kit / "template" / "_system" / "AGENTS.md.jinja"
    agents.write_text(agents.read_text(encoding="utf-8") + "\n- Regra nova da v0.2.0.\n", encoding="utf-8")
    hot_tpl = kit / "template" / "_maps" / "hot.md.jinja"
    hot_tpl.write_text(hot_tpl.read_text(encoding="utf-8") + "\n- linha nova do kit\n", encoding="utf-8")
    _git(kit, "add", "-A")
    _git(kit, "commit", "-qm", "v2")
    _git(kit, "tag", "v0.2.0")

    copier.run_update(str(cerebro), defaults=True, unsafe=True, quiet=True, overwrite=True, vcs_ref="v0.2.0")

    assert (cerebro / "_maps" / "hot.md").read_text(encoding="utf-8") == hot_cliente
    assert nota.exists()
    assert "[[06-clientes/acme]]" in mapa.read_text(encoding="utf-8")
    assert "Regra nova da v0.2.0." in (cerebro / "_system" / "AGENTS.md").read_text(encoding="utf-8")
    assert yaml.safe_load((cerebro / ".copier-answers.yml").read_text(encoding="utf-8"))["_commit"] == "v0.2.0"
