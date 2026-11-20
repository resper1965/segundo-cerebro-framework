---
name: revisao-semanal
description: Conduz a revisão semanal do cérebro — inbox zerada, hot revisado, status dos mapas, decisões da semana e prazos dos próximos 14 dias — e registra em diario/. Use uma vez por semana ou quando pedirem a revisão.
---
# revisao-semanal
1. Crie a nota em `diario/` com `_system/templates/template-revisao-semanal.md`.
2. Rode `triagem-inbox` até a inbox zerar.
3. Rode `curar-hot`.
4. Peça ao responsável o status de cada item ativo dos mapas e atualize.
5. Confirme que as decisões da semana estão em `_maps/decisoes.md`.
6. Registre vitórias, travas e foco da próxima semana.
7. Rode `python3 _system/ferramentas/brain_check.py .` e corrija.
