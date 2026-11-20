from pathlib import Path
import sys

import copier

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "extensions"))


def gerar(destino: Path, **dados) -> Path:
    base = {"nome": "Cliente Teste", "vertical": "personalizada", "modulos": [], "responsavel": "Consultor Teste"}
    base.update(dados)
    if base.get("modulos") is None:
        base.pop("modulos")
    copier.run_copy(str(KIT), str(destino), data=base, defaults=True, unsafe=True, quiet=True, vcs_ref="HEAD")
    return destino
