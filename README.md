# brain-kit
Kit da ness. para criar e implantar cérebros (segundos cérebros) empresariais e pessoais.

## Requisitos
Python 3.11+, git e as dependências de `requirements-dev.txt`.

## Gerar um cérebro
```bash
pip install -r requirements-dev.txt
copier copy --trust <url-ou-caminho-do-kit> ~/cerebros/cliente-x
```
O questionário pede nome, vertical (pessoal, empresa, jurídico, personalizada), módulos, responsável e se inclui o preset do Obsidian. Dependências de módulos entram automaticamente.

## Atualizar um cérebro existente
```bash
cd ~/cerebros/cliente-x
git switch -c update/vX.Y
copier update --trust
python3 _system/ferramentas/brain_check.py .
```
Rode as perguntas-ouro, aprove (gate) e registre em `_maps/decisoes.md` antes do merge.

## Criar um módulo
1. `modulos/<id>/modulo.yml` seguindo o contrato (ver spec §5).
2. Template de nota em `template/_system/templates/{% if '<id>' in ativos %}template-<nome>.md{% endif %}`.
3. `python3 tools/novo_modulo.py <id>` cria README da pasta e mapa.
4. Inclua o id em `choices` de `modulos` no `copier.yml`.
5. `pytest -q`.

## Testes
`pytest -q`
