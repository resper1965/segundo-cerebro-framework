"""ContextHook do Copier: injeta módulos ativos e data no contexto Jinja."""
from __future__ import annotations

import hashlib
import importlib.util
from datetime import date
from pathlib import Path

from copier_template_extensions import ContextHook

KIT = Path(__file__).resolve().parent.parent


def _carregar_lib():
    """Carrega a modulos_lib.py desta cópia do kit pelo caminho.

    No `copier update` a versão antiga e a nova do kit rodam no mesmo processo; um `import modulos_lib`
    reaproveitaria o módulo da versão antiga em sys.modules. Nome único por caminho e sem registro em
    sys.modules garantem que cada versão use a própria lib.
    """
    caminho = Path(__file__).resolve().parent / "modulos_lib.py"
    nome = "brain_kit_modulos_lib_" + hashlib.sha1(str(caminho).encode()).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(nome, caminho)
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    return lib


_lib = _carregar_lib()
carregar_fases = _lib.carregar_fases
carregar_modulos = _lib.carregar_modulos
resolver_dependencias = _lib.resolver_dependencias


class Contexto(ContextHook):
    def hook(self, context):
        modulos = carregar_modulos(KIT / "modulos")
        ativos = resolver_dependencias(context.get("modulos") or [], modulos)
        context["hoje"] = date.today().isoformat()
        context["mod"] = modulos
        context["ativos"] = ativos
        context["mods"] = [modulos[m] for m in ativos]
        context["fases"] = carregar_fases(KIT / "fases" / "nucleo.yml", context["mods"])
