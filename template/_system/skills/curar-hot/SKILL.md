---
name: curar-hot
description: Mantém o _maps/hot.md curto (até 40 linhas) e atual (até 7 dias), retirando o que esfriou e trazendo o que esquentou a partir dos mapas, prazos e rotinas. Use na revisão semanal, quando o hot estiver vencido ou quando pedirem para atualizar o contexto quente.
---
# curar-hot
1. Leia `_maps/hot.md` e `_implantacao/status.md`.
2. Para cada item: ainda está quente? Se não, mova a informação para o mapa ou nota de origem e retire do hot.
3. Traga o que esquentou: prazos dos próximos 14 dias, decisões pendentes, bloqueios, saídas das rotinas dos módulos.
4. Mantenha no máximo 40 linhas não vazias; atualize `updated`.
5. Mostre a proposta de novo hot e só grave com aprovação.
6. Rode `python3 _system/ferramentas/brain_check.py .`.
