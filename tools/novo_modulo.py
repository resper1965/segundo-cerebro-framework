#!/usr/bin/env python3
"""Cria os arquivos condicionais de um módulo (README da pasta e mapa) a partir do modulo.yml.

Uso: python3 tools/novo_modulo.py <mid> [<mid> ...]
Nunca sobrescreve arquivo existente. O template de nota do módulo é escrito à mão.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parent.parent


def criar_stubs(mid: str, kit: Path = KIT) -> list[Path]:
    kit = Path(kit)
    m = yaml.safe_load((kit / "modulos" / mid / "modulo.yml").read_text(encoding="utf-8"))
    cond = "{% if '" + mid + "' in ativos %}"
    readme = kit / "template" / (cond + m["pasta"] + "{% endif %}") / "README.md.jinja"
    mapa = kit / "template" / "_maps" / (cond + f"mapa-{mid}.md" + "{% endif %}.jinja")
    conteudos = {
        readme: "{% from 'macros/brain.jinja' import readme %}{{ readme(mod['" + mid + "']) }}\n",
        mapa: "{% from 'macros/brain.jinja' import mapa %}{{ mapa(mod['" + mid + "'], hoje) }}\n",
    }
    for caminho, texto in conteudos.items():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if not caminho.exists():
            caminho.write_text(texto, encoding="utf-8")
    return list(conteudos)


if __name__ == "__main__":
    for mid in sys.argv[1:]:
        for p in criar_stubs(mid):
            print(p.relative_to(KIT))
