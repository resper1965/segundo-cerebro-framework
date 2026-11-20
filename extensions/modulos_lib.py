"""Biblioteca de módulos do brain-kit: carregar, resolver dependências, validar contrato e montar fases."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import yaml

CAMPOS_OBRIGATORIOS = (
    "id", "nome", "descricao", "depende_de", "pasta", "entra", "nao_entra",
    "mapa", "template", "implantacao", "sistema", "agentes",
)
MODOS = {"canonico", "espelho-destilado"}
QUEM = {"consultor", "cliente", "agente"}
PASTA_RE = re.compile(r"^\d\d-[a-z0-9-]+$")


def carregar_modulos(pasta: Path) -> dict[str, dict]:
    modulos: dict[str, dict] = {}
    for arquivo in sorted(Path(pasta).glob("*/modulo.yml")):
        dados = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
        modulos[dados.get("id", arquivo.parent.name)] = dados
    return modulos


def resolver_dependencias(ativos: Iterable[str], modulos: dict[str, dict]) -> list[str]:
    resultado: set[str] = set()
    pendentes = list(ativos)
    while pendentes:
        mid = pendentes.pop()
        if mid not in modulos:
            raise ValueError(f"módulo desconhecido: {mid}")
        if mid in resultado:
            continue
        resultado.add(mid)
        pendentes.extend(modulos[mid].get("depende_de") or [])
    return sorted(resultado, key=lambda m: modulos[m].get("pasta", m))


def validar_modulos(modulos: dict[str, dict], kit: Path | None = None) -> list[str]:
    erros: list[str] = []
    pastas: dict[str, str] = {}
    ids_etapas: set[str] = set()
    for mid, m in modulos.items():
        faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in m]
        erros += [f"{mid}: campo obrigatório ausente '{c}'" for c in faltando]
        if faltando:
            continue
        for dep in m["depende_de"]:
            if dep not in modulos:
                erros.append(f"{mid}: depende de módulo inexistente '{dep}'")
        if not PASTA_RE.match(m["pasta"]):
            erros.append(f"{mid}: pasta inválida '{m['pasta']}'")
        if m["pasta"] in pastas:
            erros.append(f"pasta '{m['pasta']}' repetida em {pastas[m['pasta']]} e {mid}")
        pastas[m["pasta"]] = mid
        if not str(m["template"]).startswith("template-"):
            erros.append(f"{mid}: template deve começar com 'template-'")
        if m["sistema"].get("modo") not in MODOS:
            erros.append(f"{mid}: sistema.modo inválido '{m['sistema'].get('modo')}'")
        if not m["mapa"].get("colunas"):
            erros.append(f"{mid}: mapa sem colunas")
        for etapa in m["implantacao"]:
            eid = etapa.get("id", "?")
            if not eid.startswith(f"M-{mid}."):
                erros.append(f"{mid}: etapa '{eid}' deve começar com 'M-{mid}.'")
            if etapa.get("fase") not in range(0, 6):
                erros.append(f"{mid}: etapa '{eid}' com fase inválida {etapa.get('fase')}")
            if etapa.get("quem") not in QUEM:
                erros.append(f"{mid}: etapa '{eid}' com quem inválido '{etapa.get('quem')}'")
            if eid in ids_etapas:
                erros.append(f"{mid}: etapa '{eid}' repetida")
            ids_etapas.add(eid)
        if kit is not None:
            erros += _validar_arquivos(mid, m, Path(kit))
    return erros


def _validar_arquivos(mid: str, m: dict, kit: Path) -> list[str]:
    cond = "{% if '" + mid + "' in ativos %}"
    esperados = [
        kit / "template" / (cond + m["pasta"] + "{% endif %}") / "README.md.jinja",
        kit / "template" / "_maps" / (cond + f"mapa-{mid}.md" + "{% endif %}.jinja"),
        kit / "template" / "_system" / "templates" / (cond + f"{m['template']}.md" + "{% endif %}"),
    ]
    return [f"{mid}: arquivo ausente {p.relative_to(kit)}" for p in esperados if not p.exists()]


def carregar_fases(arquivo: Path, mods: list[dict]) -> list[dict]:
    arquivo = Path(arquivo)
    if not arquivo.exists():
        return []
    fases = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or []
    por_numero = {f["numero"]: f for f in fases}
    for f in fases:
        f["etapas"] = list(f.get("etapas") or [])
    for m in mods:
        for etapa in m.get("implantacao") or []:
            por_numero[etapa["fase"]]["etapas"].append({**etapa, "modulo": m["id"]})
    return fases
