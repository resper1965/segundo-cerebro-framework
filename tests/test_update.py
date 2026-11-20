import shutil
import subprocess
import sys

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


def _kit_v010(tmp_path):
    kit = tmp_path / "kit"
    shutil.copytree(KIT, kit, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".superpowers"))
    _git(kit, "init", "-q")
    _git(kit, "add", "-A")
    _git(kit, "commit", "-qm", "v1")
    _git(kit, "tag", "v0.1.0")
    return kit


def _rodar_isolado(codigo: str):
    """Roda copier num subprocesso limpo: sem o sys.path nem o sys.modules do conftest."""
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, cwd="/")
    assert r.returncode == 0, r.stderr[-3000:]


def test_update_usa_modulos_lib_da_versao_nova(tmp_path):
    kit = _kit_v010(tmp_path)
    cerebro = tmp_path / "cerebro"
    _rodar_isolado(
        f"import copier; copier.run_copy({str(kit)!r}, {str(cerebro)!r}, data={{'nome': 'C', 'vertical': 'pessoal', "
        f"'responsavel': 'C'}}, defaults=True, unsafe=True, quiet=True, vcs_ref='v0.1.0')")
    _git(cerebro, "init", "-q")
    _git(cerebro, "add", "-A")
    _git(cerebro, "commit", "-qm", "gerado")

    lib = kit / "extensions" / "modulos_lib.py"
    lib.write_text(lib.read_text(encoding="utf-8") + '\n\ndef versao_lib() -> str:\n    return "lib-0.2.0"\n',
                   encoding="utf-8")
    ctx = kit / "extensions" / "contexto.py"
    # carregar_modulos vem da modulos_lib; seus __globals__ são o namespace do módulo efetivamente carregado.
    ctx.write_text(ctx.read_text(encoding="utf-8").replace(
        '        context["hoje"] = date.today().isoformat()\n',
        '        context["hoje"] = date.today().isoformat()\n'
        '        context["versao_lib"] = carregar_modulos.__globals__["versao_lib"]()\n'), encoding="utf-8")
    assert "versao_lib" in ctx.read_text(encoding="utf-8")
    agents = kit / "template" / "_system" / "AGENTS.md.jinja"
    agents.write_text(agents.read_text(encoding="utf-8") + "\nVersão da lib: {{ versao_lib }}\n", encoding="utf-8")
    _git(kit, "add", "-A")
    _git(kit, "commit", "-qm", "v2")
    _git(kit, "tag", "v0.2.0")

    _rodar_isolado(f"import copier; copier.run_update({str(cerebro)!r}, defaults=True, unsafe=True, quiet=True, "
                   f"overwrite=True, vcs_ref='v0.2.0')")
    assert "Versão da lib: lib-0.2.0" in (cerebro / "_system" / "AGENTS.md").read_text(encoding="utf-8")


def test_update_que_adiciona_modulos_e_detectado_e_reconciliavel(tmp_path):
    import importlib.util
    import re
    from datetime import date

    kit = _kit_v010(tmp_path)
    cerebro = tmp_path / "cerebro"
    copier.run_copy(str(kit), str(cerebro), data={"nome": "Pessoa", "vertical": "pessoal", "responsavel": "C"},
                    defaults=True, unsafe=True, quiet=True, vcs_ref="v0.1.0")
    _git(cerebro, "init", "-q")
    _git(cerebro, "add", "-A")
    _git(cerebro, "commit", "-qm", "gerado")

    copier.run_update(str(cerebro), data={"modulos": ["objetivos", "leituras", "clientes", "propostas"]},
                      defaults=True, unsafe=True, quiet=True, overwrite=True, vcs_ref="v0.1.0")

    assert "M-propostas.1" in (cerebro / "_implantacao" / "roteiro.md").read_text(encoding="utf-8")
    spec = importlib.util.spec_from_file_location("bc_update", cerebro / "_system" / "ferramentas" / "brain_check.py")
    bc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bc)
    erros = bc.verificar(cerebro, date.today())
    assert "_implantacao/status.md: etapa M-propostas.1 do roteiro ausente" in erros

    faltando = [e.split("etapa ")[1].split(" ")[0] for e in erros if e.endswith("do roteiro ausente")]
    assert faltando and all(re.match(r"M-(clientes|ofertas|propostas)\.\d+$", i) for i in faltando)
    status = cerebro / "_implantacao" / "status.md"
    status.write_text(status.read_text(encoding="utf-8")
                      + "".join(f"| {i} | (reconciliada) | agente | não | pendente |  |\n" for i in faltando),
                      encoding="utf-8")
    assert not any("do roteiro ausente" in e for e in bc.verificar(cerebro, date.today()))
