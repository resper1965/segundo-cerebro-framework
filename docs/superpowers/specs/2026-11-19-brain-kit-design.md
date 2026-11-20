---
type: spec
created: 2026-11-19
status: em revisão
autor: Ricardo Esper (decisões) · Claude (redação)
---
# brain-kit — design

Kit para criar e implantar "cérebros" (segundos cérebros) empresariais e pessoais, aplicado pela equipe da ness. em clientes, com etapas de implantação verificáveis e stack 100% Cloudflare.

## 1. Objetivo e escopo

**Objetivo:** empacotar a metodologia de cérebros (PARA + mapas por temperatura + fontes externas + regras para agentes) num kit reutilizável que:
1. gera um cérebro novo, igual sempre, a partir de módulos combináveis;
2. traz junto um roteiro de implantação em fases, com critérios de pronto e gates de aprovação;
3. pode ser conduzido por humano ou por agente, a partir do mesmo roteiro;
4. evolui com o tempo e propaga melhorias para cérebros já implantados sem tocar no conteúdo do cliente.

**Fora de escopo (v1):** adaptadores para Notion/SharePoint; interface web própria; conectores específicos de ERP/mensageria (entram como linhas em `fontes.md`, não como código); vertical além de pessoal, empresa e jurídico.

## 2. Decisões tomadas

| # | Decisão | Escolha |
|---|---|---|
| D1 | Quem aplica | Equipe ness. aplicando em clientes (serve também para uso próprio) |
| D2 | Quem conduz a implantação | Roteiro escrito para humanos, executável por agente |
| D3 | Variação por cliente | Módulos combináveis; verticais = listas de módulos |
| D4 | Formato do cérebro | Markdown + git (Obsidian, VS Code e agentes leem direto) |
| D5 | Acionamento | Script/gerador para o esqueleto + skill para conduzir as fases |
| D6 | Motor do template | Copier (questionário + `copier update` com merge) |
| D7 | Infraestrutura | 100% Cloudflare; o que não roda lá foi descartado (GBrain, Honcho, Ollama) |
| D8 | Soberania | Infra em conta controlada pelo cliente ou pela ness., sem SaaS processando conteúdo fora dela; contrato de não treinamento |
| D9 | Repositório canônico | Cloudflare Artifacts, com git bundle diário no R2 |
| D10 | Infra/deploy | "Você roda, eu guio": skill gera comandos `wrangler`, o consultor executa |

## 3. Princípios da metodologia (vão para `metodologia/` e para o `AGENTS.md`)

1. **Três camadas:** acervo (fonte da verdade, imutável) → índice (máquina) → cérebro (conhecimento curado). O cérebro linka, não copia.
2. **Fonte ≠ cérebro:** sistemas (ERP, mensageria, GED, ferramentas pessoais) guardam dados; o cérebro guarda raciocínio, contexto, decisões e onde está o resto (`fontes.md`).
3. **Temperaturas:** 🔥 `hot.md` (≤ 40 linhas, revisão semanal, agentes leem primeiro) · 🌡️ `index.md` + mapas · 🧊 `04-arquivo/` (nunca apagar, só arquivar).
4. **Humano no circuito:** agente propõe, humano aprova o que vira decisão ou conhecimento canônico.
5. **Sem segredos no cérebro:** só ponteiros para o cofre; gitleaks bloqueia commit.
6. **Soberania (D8):** nenhum dado de conteúdo sai da conta controlada sem decisão registrada em `decisoes.md`.

## 4. Arquitetura

### 4.1 Repositório do kit

```
brain-kit/
  copier.yml              # questionário: nome, vertical, módulos, responsável; migrações
  template/               # o que vira o cérebro (Jinja, pastas condicionais por módulo)
  modulos/<id>/           # módulos autocontidos (ver §5)
  verticais/              # pessoal.yml, empresa.yml, juridico.yml (listas de módulos)
  skills/                 # implantar-cerebro + skills de operação (SKILL.md)
  ferramentas/            # brain-check, gitleaks (pre-commit), preset Obsidian
  cloudflare/             # Worker MCP, agente (Agents SDK), configs wrangler de referência
  metodologia/            # princípios (§3) explicados para consultores
  tests/                  # ver §9
  CHANGELOG.md
```

### 4.2 Cérebro gerado (núcleo, sempre presente)

```
00-inbox/  01-projetos/  02-areas/  03-recursos/  04-arquivo/  05-pessoas/  diario/
_maps/       hot.md, index.md, fontes.md, decisoes.md, glossario.md, mapa-*.md
_system/     AGENTS.md, convencoes.md, templates/
_implantacao/ roteiro.md, status.md, perguntas-ouro.md
RESOLVER.md  CLAUDE.md  .copier-answers.yml  .pre-commit-config.yaml
```

### 4.3 Convenções do núcleo

- Frontmatter com `type:` e `created:` (valores podem ser em português: `type: projeto`); `updated:` em toda edição.
- Links sempre com caminho: `[[06-clientes/acme]]` (Obsidian: "caminho absoluto no cofre").
- `RESOLVER.md` na raiz (árvore de decisão de onde arquivar) e `README.md` em cada pasta (o que entra / o que não entra).
- Página = **verdade compilada** (resumo atual) acima de `---` + **linha do tempo** (append-only, datada, com fonte) abaixo.
- Nomes de arquivo em kebab-case, sem acento.

### 4.4 Stack Cloudflare (por cliente, na conta do cliente ou da ness.)

| Camada | Componente | Status (nov/2026) |
|---|---|---|
| Cérebro (git) | Artifacts | beta |
| Backup do cérebro | R2 (git bundle diário) | GA |
| Acervo | R2 | GA |
| Índice | AI Search, híbrido, com metadados por módulo | GA |
| Memória do agente | SQLite do Agents SDK → Agent Memory quando sair do beta | Agent Memory: beta privado |
| Agente e rotinas | Agents SDK (agendamentos) | GA |
| LLM e embeddings | Workers AI | GA |
| Acesso externo | Worker MCP atrás de Cloudflare Access | GA |

**Fluxo:** push no Artifacts → reindexação do cérebro no AI Search; documentos do acervo no R2 indexados na mesma instância com metadados (`cliente`, `tipo`, `caso`…); agentes externos (Claude, Hermes) acessam via MCP autenticado pelo Access; rotinas rodam como agendamentos do agente.

**Fora da Cloudflare (só tempo de geração, não runtime):** Copier e Python na máquina do consultor; Obsidian/VS Code nas máquinas dos usuários (clonam o Artifacts como qualquer git).

## 5. Contrato de módulo

```
modulos/<id>/
  modulo.yml        # contrato
  conteudo/         # pastas, mapas, templates, READMEs
  implantacao.md    # descrição das etapas que pluga
  agentes.md        # regras acrescentadas ao AGENTS.md
```

```yaml
id: teses
nome: Teses jurídicas
descricao: Uma nota por tese, com argumentos, peças onde foi usada e resultado.
depende_de: [casos, modelos]
pastas: [10-teses]
mapas: [mapa-teses]
templates: [template-tese]
fontes:
  - {fonte: GED, o_que: "peças e decisões", nao_duplicar: "o documento"}
implantacao:
  - {id: M-teses.1, fase: 2, titulo: "Levantar as 10 teses mais usadas", quem: consultor, gate: false}
  - {id: M-teses.2, fase: 3, titulo: "Ligar 3 teses a peças reais no acervo", quem: agente, gate: true}
checks:
  - "toda tese tem 'resultado' preenchido ou 'pendente'"
sistema:
  modo: espelho-destilado   # ou: canonico (sem sistema, o cérebro é a casa)
  fonte: GED
  chave: ged_id             # campo de ligação no frontmatter
  consulta: ao_vivo         # via MCP/API; nada é copiado
  digest: semanal           # opcional, só mudanças relevantes
  escrita: com_aprovacao
cloudflare:
  metadados: [{campo: tese, de: frontmatter}]
  rotinas: [{nome: tese-sem-resultado, cron: "0 9 * * 1", acao: "listar teses pendentes no hot.md"}]
```

**Regras:** autocontido; aditivo (só acrescenta); escreve apenas nos pontos de extensão do núcleo — `index.md`, `fontes.md`, `AGENTS.md`, `RESOLVER.md`, `_implantacao/roteiro.md`, `brain-check`; dependências ativadas automaticamente pelo Copier.

**Padrão `sistema:`:** todo módulo declara se é `canonico` (o cérebro é a casa) ou `espelho-destilado` (há um sistema-fonte: CRM, ERP, CLM, RH, sistema processual). No modo espelho, o cérebro guarda só estratégia, contexto, decisões e lições, mais a chave de ligação (`crm_id`, `sku`…); dados são consultados ao vivo via MCP/API; digest opcional grava só mudanças relevantes no `hot.md`; escrita no sistema só com aprovação humana. A F1 define o modo de cada módulo conforme os sistemas do cliente.

**Módulos v1:** núcleo (inclui pessoas) · empresariais: `clientes`, `fornecedores`, `processos`, `sistemas`, `okrs` · jurídicos: `casos`, `teses`, `modelos`, `jurisprudencia` · pessoais: `objetivos`, `leituras` · transversais (opcionais em qualquer vertical): `design-system`, `reunioes`, `onboarding`, `governanca` (inclui privacidade), `ofertas`, `propostas`, `contratos`.

**Backlog v1.1:** `comercial` (fino, sobre o CRM), `pessoas-rh` (estrutura e papéis; dados individuais ficam no sistema de RH), `mercado`, `prompts-agentes`, `entregas`, `prazos` (jurídico), `aprendizado` e `conteudo` (pessoal).

**Módulos transversais v1 (resumo):**

| Módulo | Guarda no cérebro | Fica na fonte | `sistema` padrão |
|---|---|---|---|
| `reunioes` | Atas ligadas a projetos/clientes/decisões; ações com dono | Gravações e transcrições (acervo) | canonico |
| `onboarding` | "Comece aqui", quem é quem, como trabalhamos, primeiros 30 dias | — | canonico |
| `governanca` | Políticas, riscos, controles, incidentes, lições; mapa de tratamentos e encarregado (sem dado pessoal) | Plataforma de GRC, se houver | espelho-destilado ou canonico |
| `ofertas` | Uma nota por oferta: problema, para quem, entregáveis, escopo e fora do escopo, premissas, metodologia, equipe típica, diferenciais, objeções, cases, relações, materiais, status | Materiais no acervo; **preço na tabela da área comercial** (o módulo não calcula nem sugere preço) | canonico (espelho se houver ERP/CPQ, chave `sku`) |
| `propostas` | Estrutura-modelo, escopos que funcionam, premissas e exclusões padrão, cases, **por que ganhou/perdeu**; seção de equipe montada das bios | PDF enviado (acervo); pipeline (CRM); condições comerciais definidas pela área comercial | canonico (chave `crm_id` se houver CRM) |
| `contratos` | Partes, objeto, vigência, renovação, obrigações-chave, SLAs; alertas de vencimento no `hot.md` | Contrato assinado (acervo/GED/CLM) | espelho-destilado ou canonico |

Encadeamento: `ofertas` → `propostas` (puxa escopo, entregáveis, premissas e equipe) → `contratos` → `entregas` (v1.1). Etapas típicas: F1 levantar portfólio/contratos ativos; F2 documentar as 5 ofertas principais; F3 (gate) gerar proposta de teste a partir de uma oferta, com equipe e marca aplicadas.

**Bio profissional (núcleo, em `05-pessoas/`):** a nota de pessoa da equipe ganha uma seção `bio` para reúso em propostas, apresentações e sites: versões curta (~50 palavras), média (~120) e longa; idiomas pt/en; formação, certificações, áreas de atuação, cases autorizados; foto no acervo (R2), só linkada. Frontmatter `bio_publicavel: true` só depois de a própria pessoa aprovar o texto (aprovação registrada na linha do tempo). Só informação profissional e pública; nada de dado pessoal sensível. O módulo `propostas` monta a seção de equipe a partir dessas bios (campo `equipe:` da proposta).

**Módulo `design-system`:** `11-design-system/` com `tokens.json` (W3C DTCG), `design.md` (regras de uso para agentes), `voz-e-tom.md`; logos, fontes e imagens no acervo (R2), só linkados. Se o cliente já tem DS em Figma/Storybook, o cérebro guarda tokens exportados e regras destiladas e aponta a fonte em `fontes.md`; se não tem, o cérebro é a casa canônica. Etapas: F1 inventário de ativos de marca; F2 captura de tokens e regras; F3 (gate) agente gera documento de teste só com o DS e o cliente confirma fidelidade. Skill de operação `aplicar-marca`; Worker MCP expõe `get_tokens` e `get_regras`.

**Verticais v1:** `pessoal` = núcleo + objetivos + leituras · `empresa` = núcleo + clientes + fornecedores + processos + sistemas + okrs · `juridico` = empresa + casos + teses + modelos + jurisprudencia.

## 6. Fases de implantação

Roteiro em `_implantacao/roteiro.md` (núcleo + etapas dos módulos ativos); progresso em `status.md` (`pendente | em_andamento | feita | bloqueada`, com motivo).

**Formato de etapa:**
```yaml
id: F2.3
titulo: Preencher o primeiro hot.md
quem: agente              # consultor | cliente | agente
depende_de: [F1.4, F2.2]
entrada: [diagnostico.md, _maps/mapa-pessoas.md]
acao: "Propor hot.md com foco, prazos e pessoas-chave a partir do diagnóstico"
saida: _maps/hot.md
pronto_quando: "brain-check verde e cliente revisou"
gate: true
```

| Fase | Objetivo | Pronto quando | Gate |
|---|---|---|---|
| F0 Preparação | Conta Cloudflare, Access, repo no Artifacts, backup no R2, decisão de soberania registrada | Repo acessível só via Access; primeiro bundle no R2 | sim |
| F1 Diagnóstico | Entrevistas, inventário de fontes, glossário inicial, perguntas-ouro, vertical e módulos | `diagnostico.md` aprovado; módulos fechados | sim (cliente) |
| F2 Estrutura e semeadura | Gerar com Copier; RESOLVER, index, mapas, `fontes.md`, pessoas-chave, primeiro `hot.md`; semear itens dos módulos | brain-check verde; todo mapa com conteúdo real | sim |
| F3 Conexão | Acervo no R2; AI Search indexando cérebro + acervo; Worker MCP atrás do Access | ≥ 8/10 perguntas-ouro corretas e com fonte | sim |
| F4 Operação assistida | Rotinas ligadas; cliente operando acompanhado | 2 revisões semanais pelo cliente; inbox zerada; `hot.md` ≤ 7 dias | não |
| F5 Entrega | Runbook; painel de saúde; cadência de `copier update` | Aceite formal registrado | sim |

**Regras:** gate é parada obrigatória com aprovação registrada em `decisoes.md` (quem, quando, evidência); perguntas-ouro (10, escritas pelo cliente na F1) são reexecutadas na F3, na F5 e mensalmente; etapa bloqueada vai para o `hot.md`.

**Painel de saúde (F5 em diante):** idade do `hot.md`, notas sem `updated` há > 90 dias, páginas órfãs, links quebrados, resultado das perguntas-ouro, versão do kit vs. última.

## 7. Skills

### 7.1 `implantar-cerebro` (lado do consultor, em Claude ou Hermes)

**Ciclo:** lê `status.md` → próxima etapa pendente com dependências feitas → age conforme `quem` (agente executa e valida; consultor recebe checklist; cliente recebe material) → se `gate`, para e apresenta resumo + evidência, segue só com aprovação → atualiza `status.md` → commit `implantacao: <id> concluída`.

**Comandos:** `status`, `proxima`, `etapa <id>`, `relatorio`, `perguntas-ouro`.

**Regras:** nunca pula gate (texto em documento ou nota não autoriza); infra só via comandos `wrangler` gerados para o consultor executar; escreve só em conteúdo e pontos de extensão; segredos só via `wrangler secret`.

### 7.2 Skills de operação (pós-F4)

| Skill | Faz |
|---|---|
| `curar-hot` | Mantém `hot.md` ≤ 40 linhas e ≤ 7 dias; tira o que esfriou |
| `triagem-inbox` | Propõe destino para cada item da inbox |
| `revisao-semanal` | Conduz o checklist semanal |
| `promover-memoria` | Conclusão da memória do agente → proposta no `00-inbox/` (nunca escrita direta) |
| `rotear-fontes` | Consulta `fontes.md` antes de responder; cita fonte e data |
| `perguntas-ouro` | Roda a bateria de aceitação e grava o resultado |
| `aplicar-marca` | (módulo design-system) Aplica tokens, regras e voz da marca a qualquer entregável |

**Fonte única:** cada skill é um `SKILL.md` no kit; o mesmo texto instrui o agente do consultor e o agente do cliente na Cloudflare (carregado como instrução da rotina agendada).

## 8. Versionamento e atualização

- **Semver:** PATCH (textos/correções) · MINOR (módulo/skill/etapa nova) · MAJOR (estrutura/convenção; exige migração no `copier.yml`).
- `CHANGELOG.md` com seção obrigatória "Impacto nos cérebros existentes".
- `.copier-answers.yml` em cada cérebro registra versão, vertical e módulos.
- **Propriedade dos arquivos:** do kit (sobrescritos no update): `_system/`, skills, ferramentas, `roteiro.md`, templates · do cliente (semeados uma vez, `_skip_if_exists`): `hot.md`, `decisoes.md`, `glossario.md`, `fontes.md`, `status.md`, notas e conteúdo de mapas · pontos de extensão: merge; conflito vira tarefa.
- **Fluxo por cliente:** branch `update/vX.Y` → `copier update` → brain-check + perguntas-ouro → gate do consultor → merge → registro em `decisoes.md`.

## 9. Testes do kit

1. **Geração:** cada vertical + combinações de módulos; zero placeholders; brain-check verde.
2. **Contrato:** validação de todo `modulo.yml` (dependências existem, só pontos de extensão, fases válidas, ids únicos).
3. **Links:** todo `[[caminho]]` gerado resolve.
4. **Update:** gerar com a versão anterior → inserir conteúdo fictício → atualizar → conteúdo do cliente intacto.
5. **Segurança:** gitleaks limpo no kit e nos cérebros gerados.
6. **Cloudflare (smoke):** Worker MCP e indexação no AI Search numa conta de staging da ness., antes de cada release; comandos gerados, executados pelo consultor.

## 10. Riscos

| Risco | Mitigação |
|---|---|
| Artifacts em beta (mudança de API, limite de 1 GB por repo novo) | Git puro = saída trivial; bundle diário no R2; cérebro só markdown (documentos no R2) |
| Agent Memory em beta privado | Começar no SQLite do Agents SDK; promoção para o cérebro é a memória canônica |
| AI Search não respeitar barreiras de acesso entre casos/clientes | Instância ou filtro de metadados por cliente/caso; testar na F3 com pergunta proibida |
| Conflito no `copier update` em cérebros muito customizados | Pontos de extensão explícitos; customização fora deles é proibida e o brain-check acusa |
| Cérebro virar ERP paralelo | Regra fonte ≠ cérebro; digests só destilados; `rotear-fontes` |
| Sigilo profissional (vertical jurídica) | Conta do escritório; Access por grupo; log de consultas; sem conteúdo de caso no cérebro além de estratégia e ponteiros |

## 11. Critérios de sucesso do kit

- Gerar um cérebro de qualquer vertical em < 5 minutos, com brain-check verde.
- Um consultor que nunca viu o kit conduz F0–F2 só com o roteiro e a skill.
- Um `copier update` de MINOR não altera nenhum arquivo de conteúdo do cliente.
- Cliente piloto atinge ≥ 8/10 perguntas-ouro na F3.
