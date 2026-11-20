"""ContextHook do Copier: injeta módulos ativos e data no contexto Jinja."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from copier_template_extensions import ContextHook  # noqa: E402

from modulos_lib import carregar_modulos, resolver_dependencias  # noqa: E402

KIT = Path(__file__).resolve().parent.parent


class Contexto(ContextHook):
    def hook(self, context):
        modulos = carregar_modulos(KIT / "modulos")
        ativos = resolver_dependencias(context.get("modulos") or [], modulos)
        context["hoje"] = date.today().isoformat()
        context["mod"] = modulos
        context["ativos"] = ativos
        context["mods"] = [modulos[m] for m in ativos]
