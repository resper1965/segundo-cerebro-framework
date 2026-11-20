#!/usr/bin/env python3
"""brain-check: valida um cérebro gerado pelo brain-kit (frontmatter, links, hot.md, placeholders).

Uso: python3 _system/ferramentas/brain_check.py <raiz> [--hoje AAAA-MM-DD] [--estrito]
Só biblioteca padrão. Código de saída 0 = verde, 1 = há erros. Avisos (hot.md vencido) não mudam o código,
salvo com --estrito, que os trata como erro.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

IGNORAR_PREFIXOS = (("_system", "templates"), ("_system", "skills"), ("_system", "ferramentas"))
SEM_FRONTMATTER_PASTAS = {"00-inbox"}
EXTENSAO = re.compile(r"\.(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{1,5}$")
SEM_FRONTMATTER = {"README.md", "RESOLVER.md", "CLAUDE.md", "AGENTS.md"}
PASTA_CONTEUDO = re.compile(r"^(\d\d-[a-z0-9-]+|diario|_maps|_implantacao)$")
LINK = re.compile(r"\[\[([^\]|#]*)(?:[#|][^\]]*)?\]\]")
BLOCO_CODIGO = re.compile(r"```.*?```", re.S)
CODIGO_INLINE = re.compile(r"`[^`\n]*`")
MAX_LINHAS_HOT = 40
MAX_DIAS_HOT = 7
ID_ETAPA = r"(F\d+\.\d+|M-[a-z0-9-]+\.\d+)"
BLOCO_YAML = re.compile(r"```yaml\n(.*?)```", re.S)
ID_ROTEIRO = re.compile(r"^\s*(?:-\s+)?id:\s*" + ID_ETAPA + r"\s*$", re.M)
ID_STATUS = re.compile(r"^\|\s*" + ID_ETAPA + r"\s*\|", re.M)


def ler_frontmatter(texto: str) -> tuple[dict | None, str]:
    texto = texto.replace("\r\n", "\n")
    if not texto.startswith("---\n"):
        return None, texto
    fecho = re.search(r"^---$", texto[4:], re.M)
    if fecho is None:
        return None, texto
    dados: dict[str, str] = {}
    for linha in texto[4:4 + fecho.start()].splitlines():
        if ":" in linha and not linha.startswith((" ", "-", "#")):
            chave, valor = linha.split(":", 1)
            dados[chave.strip()] = valor.strip().strip("'\"")
    return dados, texto[4 + fecho.end():].lstrip("\n")


def _sem_codigo(texto: str) -> str:
    return CODIGO_INLINE.sub("", BLOCO_CODIGO.sub("", texto))


def _arquivos(raiz: Path):
    for caminho in sorted(raiz.rglob("*.md")):
        rel = caminho.relative_to(raiz)
        if any(parte.startswith(".") for parte in rel.parts[:-1]):
            continue
        if len(rel.parts) > 2 and rel.parts[:2] in IGNORAR_PREFIXOS:
            continue
        yield caminho, rel


def verificar(raiz: Path, hoje: date, estrito: bool = False) -> list[str]:
    raiz = Path(raiz)
    erros: list[str] = []
    for caminho, rel in _arquivos(raiz):
        nome = rel.as_posix()
        try:
            texto = caminho.read_text(encoding="utf-8").replace("\r\n", "\n")
        except UnicodeDecodeError:
            erros.append(f"{nome}: não é UTF-8")
            continue
        limpo = _sem_codigo(texto)
        if "{{" in limpo or "}}" in limpo:
            erros.append(f"{nome}: placeholder não resolvido")
        fm, _ = ler_frontmatter(texto)
        em_conteudo = len(rel.parts) > 1 and PASTA_CONTEUDO.match(rel.parts[0]) and rel.parts[0] not in SEM_FRONTMATTER_PASTAS
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
            elif not (raiz / (alvo if EXTENSAO.search(alvo) else f"{alvo}.md")).exists():
                erros.append(f"{nome}: link quebrado [[{alvo}]]")
    erros += _verificar_hot(raiz)
    erros += _verificar_status(raiz)
    if estrito:
        erros += avisos(raiz, hoje)
    return erros


def avisos(raiz: Path, hoje: date) -> list[str]:
    """Problemas que não bloqueiam commit (viram erro com --estrito): hot.md vencido."""
    fm, _ = _ler_hot(Path(raiz))
    try:
        atualizado = date.fromisoformat((fm or {}).get("updated", ""))
    except ValueError:
        return []
    dias = (hoje - atualizado).days
    return [f"_maps/hot.md: vencido ({dias} dias)"] if dias > MAX_DIAS_HOT else []


def _ler_hot(raiz: Path) -> tuple[dict | None, str]:
    hot = raiz / "_maps" / "hot.md"
    if not hot.exists():
        return None, ""
    return ler_frontmatter(hot.read_text(encoding="utf-8", errors="replace"))


def _verificar_status(raiz: Path) -> list[str]:
    roteiro = raiz / "_implantacao" / "roteiro.md"
    status = raiz / "_implantacao" / "status.md"
    if not (roteiro.exists() and status.exists()):
        return []
    texto_roteiro = roteiro.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    ids_roteiro = [i for bloco in BLOCO_YAML.findall(texto_roteiro) for i in ID_ROTEIRO.findall(bloco)]
    ids_status = set(ID_STATUS.findall(status.read_text(encoding="utf-8", errors="replace")))
    return [f"_implantacao/status.md: etapa {i} do roteiro ausente" for i in ids_roteiro if i not in ids_status]


def _verificar_hot(raiz: Path) -> list[str]:
    if not (raiz / "_maps" / "hot.md").exists():
        return ["_maps/hot.md: ausente"]
    erros: list[str] = []
    fm, corpo = _ler_hot(raiz)
    linhas = [linha for linha in corpo.splitlines() if linha.strip()]
    if len(linhas) > MAX_LINHAS_HOT:
        erros.append(f"_maps/hot.md: {len(linhas)} linhas (máx. {MAX_LINHAS_HOT})")
    try:
        date.fromisoformat((fm or {}).get("updated", ""))
    except ValueError:
        erros.append("_maps/hot.md: 'updated' ausente ou inválido")
    return erros


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida um cérebro do brain-kit.")
    parser.add_argument("raiz", nargs="?", default=".")
    parser.add_argument("--hoje", default=None, help="data de referência AAAA-MM-DD (padrão: hoje)")
    parser.add_argument("--estrito", action="store_true", help="trata avisos (hot.md vencido) como erro")
    args = parser.parse_args(argv)
    hoje = date.fromisoformat(args.hoje) if args.hoje else date.today()
    erros = verificar(Path(args.raiz), hoje, estrito=args.estrito)
    if not args.estrito:
        for aviso in avisos(Path(args.raiz), hoje):
            print(f"AVISO {aviso}")
    for erro in erros:
        print(f"ERRO {erro}")
    print("brain-check: verde" if not erros else f"brain-check: {len(erros)} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
