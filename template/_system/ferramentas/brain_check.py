#!/usr/bin/env python3
"""brain-check: valida um cérebro gerado pelo brain-kit (frontmatter, links, hot.md, placeholders).

Uso: python3 _system/ferramentas/brain_check.py <raiz> [--hoje AAAA-MM-DD]
Só biblioteca padrão. Código de saída 0 = verde, 1 = há erros.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

IGNORAR_DIRS = {".git", ".obsidian", "templates", "skills", "ferramentas"}
SEM_FRONTMATTER = {"README.md", "RESOLVER.md", "CLAUDE.md", "AGENTS.md"}
PASTA_CONTEUDO = re.compile(r"^(\d\d-[a-z0-9-]+|diario|_maps|_implantacao)$")
LINK = re.compile(r"\[\[([^\]|#]*)(?:[#|][^\]]*)?\]\]")
BLOCO_CODIGO = re.compile(r"```.*?```", re.S)
CODIGO_INLINE = re.compile(r"`[^`\n]*`")
MAX_LINHAS_HOT = 40
MAX_DIAS_HOT = 7


def ler_frontmatter(texto: str) -> tuple[dict | None, str]:
    if not texto.startswith("---\n"):
        return None, texto
    fim = texto.find("\n---", 4)
    if fim == -1:
        return None, texto
    dados: dict[str, str] = {}
    for linha in texto[4:fim].splitlines():
        if ":" in linha and not linha.startswith((" ", "-", "#")):
            chave, valor = linha.split(":", 1)
            dados[chave.strip()] = valor.strip().strip("'\"")
    return dados, texto[fim + 4:].lstrip("\n")


def _sem_codigo(texto: str) -> str:
    return CODIGO_INLINE.sub("", BLOCO_CODIGO.sub("", texto))


def _arquivos(raiz: Path):
    for caminho in sorted(raiz.rglob("*.md")):
        rel = caminho.relative_to(raiz)
        if any(parte in IGNORAR_DIRS for parte in rel.parts[:-1]):
            continue
        yield caminho, rel


def verificar(raiz: Path, hoje: date) -> list[str]:
    raiz = Path(raiz)
    erros: list[str] = []
    for caminho, rel in _arquivos(raiz):
        nome = rel.as_posix()
        texto = caminho.read_text(encoding="utf-8")
        limpo = _sem_codigo(texto)
        if "{{" in limpo or "}}" in limpo:
            erros.append(f"{nome}: placeholder não resolvido")
        fm, _ = ler_frontmatter(texto)
        em_conteudo = len(rel.parts) > 1 and PASTA_CONTEUDO.match(rel.parts[0])
        if em_conteudo and rel.name not in SEM_FRONTMATTER:
            if fm is None:
                erros.append(f"{nome}: sem frontmatter")
            else:
                for campo in ("type", "created"):
                    if not fm.get(campo):
                        erros.append(f"{nome}: frontmatter sem '{campo}'")
        for alvo in LINK.findall(limpo):
            alvo = alvo.strip()
            if not alvo:
                erros.append(f"{nome}: link vazio")
            elif "/" not in alvo:
                erros.append(f"{nome}: link sem caminho [[{alvo}]]")
            elif not (raiz / (alvo if alvo.endswith(".md") else f"{alvo}.md")).exists():
                erros.append(f"{nome}: link quebrado [[{alvo}]]")
    erros += _verificar_hot(raiz, hoje)
    return erros


def _verificar_hot(raiz: Path, hoje: date) -> list[str]:
    hot = raiz / "_maps" / "hot.md"
    if not hot.exists():
        return ["_maps/hot.md: ausente"]
    erros: list[str] = []
    fm, corpo = ler_frontmatter(hot.read_text(encoding="utf-8"))
    linhas = [linha for linha in corpo.splitlines() if linha.strip()]
    if len(linhas) > MAX_LINHAS_HOT:
        erros.append(f"_maps/hot.md: {len(linhas)} linhas (máx. {MAX_LINHAS_HOT})")
    try:
        atualizado = date.fromisoformat((fm or {}).get("updated", ""))
    except ValueError:
        erros.append("_maps/hot.md: 'updated' ausente ou inválido")
    else:
        dias = (hoje - atualizado).days
        if dias > MAX_DIAS_HOT:
            erros.append(f"_maps/hot.md: vencido ({dias} dias)")
    return erros


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida um cérebro do brain-kit.")
    parser.add_argument("raiz", nargs="?", default=".")
    parser.add_argument("--hoje", default=None, help="data de referência AAAA-MM-DD (padrão: hoje)")
    args = parser.parse_args(argv)
    hoje = date.fromisoformat(args.hoje) if args.hoje else date.today()
    erros = verificar(Path(args.raiz), hoje)
    for erro in erros:
        print(f"ERRO {erro}")
    print("brain-check: verde" if not erros else f"brain-check: {len(erros)} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
