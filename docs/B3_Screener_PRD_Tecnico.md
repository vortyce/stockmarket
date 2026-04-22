# B3 Screener — PRD Técnico e Guia de Implementação

## 1. Visão do produto

O B3 Screener é um sistema de triagem quantitativa para ações da bolsa brasileira.

O objetivo não é executar compra automática. O objetivo é:

- ingerir dados contábeis e de mercado
- consolidar métricas por empresa
- calcular score por setor
- gerar rankings e buckets
- expor os resultados por API
- exibir dashboards
- usar agentes apenas para explicação, automação e interpretação auxiliar

## 2. Objetivo principal

Responder com consistência:

- quais ações estão mais atraentes segundo o modelo
- por que estão no ranking
- quais riscos exigem revisão
- quais ativos entraram ou saíram do top 20
- quais nomes são value traps

## 3. Princípios do sistema

1. O score oficial precisa ser determinístico.
2. O cálculo precisa ser auditável e reproduzível.
3. Toda rodada relevante precisa gerar snapshot histórico.
4. Agentes não podem alterar o score oficial.
5. Dados oficiais e dados complementares precisam ficar separados.
6. Dashboard vem depois de dados, motor e ranking.

## 4. Escopo funcional

### Entradas
- dados contábeis históricos
- dados de mercado atuais
- classificação setorial
- regras de score por setor
- penalizações e red flags

### Processamento
- consolidação histórica
- cálculo de métricas
- cálculo de score bruto
- ponderação setorial
- aplicação de penalizações
- geração de ranking
- classificação em buckets

### Saídas
- top 20 geral
- rankings por setor
- rankings por tese
- lista de armadilhas de valor
- histórico de score
- análise textual assistida por agente

## 5. Arquitetura recomendada

### Backend
- Python
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic
- PostgreSQL
- Redis

### Frontend
- Next.js
- TypeScript

### Jobs
- scripts Python no MVP
- Celery ou RQ depois

### Infra
- Docker
- Docker Compose

### Camada agentic
- Hermes, Antigravity ou OpenClaw apenas para:
  - explicação
  - briefing
  - automação
  - alertas
  - comentários por tese e por ranking

## 6. Regra central sobre agentes

O agente pode:

- resumir teses
- explicar mudanças
- comentar riscos
- gerar briefing semanal
- organizar tarefas de revisão

O agente não pode:

- calcular o score canônico
- decidir o ranking oficial
- substituir o motor quantitativo

## 7. Estrutura de repositório

```text
b3-screener/
  backend/
    app/
      api/
      core/
      db/
      models/
      repositories/
      schemas/
      services/
      jobs/
      main.py
    alembic/
    tests/
    requirements.txt
    Dockerfile
  frontend/
    app/
    components/
    lib/
    types/
    package.json
    Dockerfile
  infra/
    docker-compose.yml
  docs/
    architecture.md
    api-contract.md
    scoring-model.md
    implementation-guide.md
```

## 8. Entidades do domínio

### companies
Cadastro da empresa.

Campos principais:
- ticker
- company_name
- cnpj
- cvm_code
- sector
- subsector
- listing_segment
- main_index
- free_float
- avg_daily_liquidity
- is_active

### financials_annual
Histórico anual por empresa.

Campos principais:
- year
- revenue
- ebit
- net_income
- cfo
- fcf
- dividends
- equity
- net_debt
- ebitda
- ebit_margin
- net_margin
- roe
- roic
- payout
- eps
- bvps

### market_snapshots
Métricas de mercado correntes.

Campos principais:
- as_of_date
- price
- pe
- pb
- ev_ebitda
- fcf_yield
- dividend_yield
- pe_5y_avg
- pb_5y_avg
- ev_ebitda_5y_avg
- sector_pe_avg
- sector_pb_avg
- sector_ev_ebitda_avg
- graham_number
- graham_discount
- simple_fair_value
- fair_value_discount

### trend_snapshots
Sinais de tendência.

Campos principais:
- revenue_yoy
- ebit_yoy
- net_income_yoy
- ebit_margin_current
- ebit_margin_previous
- margin_delta
- net_debt_current
- net_debt_previous
- debt_delta
- buyback_flag
- guidance_flag
- earnings_revision_flag
- improvement_flag

### risk_flags
Penalizações e red flags.

Campos principais:
- non_recurring_profit_penalty
- recurring_negative_fcf_penalty
- debt_up_income_down_penalty
- unsustainable_payout_penalty
- margin_deterioration_penalty
- governance_penalty
- binary_event_penalty
- accounting_penalty
- total_penalty

### sector_configs
Configuração por setor.

Campos principais:
- sector
- weight_quality
- weight_valuation
- weight_dividends
- weight_trend
- weight_gov_liq
- use_debt_ebitda
- use_pb_strong
- use_dividend_strong
- notes

### score_snapshots
Resultado do score por empresa e data.

Campos principais:
- quality_raw
- valuation_raw
- dividends_raw
- trend_raw
- gov_liq_raw
- quality_weighted
- valuation_weighted
- dividends_weighted
- trend_weighted
- gov_liq_weighted
- penalty
- final_score
- rating_class
- bucket
- summary

### ranking_snapshots
Ranking consolidado por data e escopo.

Campos principais:
- as_of_date
- scope
- position
- company_id
- final_score
- bucket
- rating_class

## 9. Fontes de dados

### Fontes estruturais
- CVM para dados contábeis e históricos
- B3 para cadastro, setor, segmento e índices

### Fontes complementares
- provider de mercado para preço e múltiplos
- no MVP, provider protótipo
- depois, provider robusto

### Regra
Separar sempre:
- dado oficial estrutural
- dado complementar operacional

## 10. Pipeline de dados

1. baixar e consolidar dados da CVM
2. atualizar cadastro da B3
3. enriquecer mercado
4. calcular benchmarks setoriais
5. calcular score
6. gerar ranking
7. salvar snapshots
8. expor via API
9. renderizar dashboards
10. gerar análise textual auxiliar

## 11. Frequência recomendada

- mercado: semanal
- score geral: mensal
- revisão estrutural: após novos resultados trimestrais ou anuais

## 12. Modelo de scoring

### Blocos de score
- qualidade
- valuation
- dividendos
- tendência
- governança/liquidez

### Penalizações
- lucro não recorrente
- FCF negativo recorrente
- dívida subindo com lucro caindo
- payout insustentável
- margem deteriorando
- governança ruim
- evento binário
- contabilidade confusa

### Buckets
- Qualidade com Desconto
- Deep Value
- Renda Defensiva
- Rerating
- Value Trap
- Financeiro Defensivo
- Cíclica Descontada
- Recuperação Operacional
- Neutro

## 13. Regras por setor

Exemplos:
- bancos: mais peso em qualidade, P/VP e dividendos
- seguradoras: lógica próxima de bancos
- elétricas: mais peso em dividendos e previsibilidade
- saneamento e concessões: mais peso em tendência e renda
- commodities: mais peso em valuation
- varejo: mais peso em tendência e recuperação
- holdings: mais peso em valuation e P/VP

## 14. Contrato mínimo de API

### Health
`GET /health`

### Companies
`GET /companies`
`GET /companies/{ticker}`

### Scores
`GET /scores/{ticker}`

### Rankings
`GET /rankings/top20`
`GET /rankings/by-sector?sector=BANCOS`
`GET /rankings/history?ticker=BBAS3`

### Jobs
`POST /jobs/ingest`
`POST /jobs/recalculate`

### Alerts
`GET /alerts`

## 15. Responsabilidade por módulo no backend

### models
Mapeamento das tabelas.

### schemas
Validação de entrada e saída.

### repositories
Acesso ao banco.

### services
Lógica de:
- scoring
- ranking
- benchmarks
- enriquecimento

### jobs
Execução de:
- ingestão
- recálculo
- rankings
- alertas

### api/routes
Exposição REST.

## 16. Ingestão

### Ingestão CVM
Deve:
- baixar arquivos
- extrair ZIPs
- consolidar demonstrativos
- persistir histórico anual

### Ingestão B3
Deve:
- atualizar cadastro
- setor
- subsetor
- segmento
- índice

### Regras da ingestão
- ser idempotente
- ter logs
- suportar falha parcial
- não duplicar registros

## 17. Enriquecimento de mercado

### Objetivo
Popular:
- price
- pe
- pb
- ev_ebitda
- fcf_yield
- dividend_yield
- graham_number
- descontos
- valor justo simples

### Regra
Se faltar dado, gravar nulo e seguir.

### Histórico de múltiplos
No MVP:
- P/L médio 5 anos
- P/VP médio 5 anos

EV/EBITDA histórico pode ficar para fase posterior.

## 18. Motor de scoring

### Requisitos
- determinístico
- testável
- modular
- independente do frontend
- independente do agente

### Saída mínima
- raw por bloco
- weighted por bloco
- penalty
- final_score
- rating_class
- bucket
- summary

### Testes obrigatórios
- banco
- seguradora
- elétrica
- commodity
- varejo
- industrial
- holding

## 19. Ranking engine

### Rankings necessários
- geral
- por setor
- por bucket
- renda defensiva
- deep value
- rerating
- value traps

### Histórico
Toda rodada gera snapshot novo.

### Comparação temporal
Detectar:
- entrou no top 20
- saiu do top 20
- subiu score
- caiu score
- mudou bucket

## 20. Frontend

### Home
- top 20
- mudanças recentes
- buckets

### Screener
Filtros por:
- setor
- score
- bucket
- desconto
- DY
- liquidez

### Detalhe da empresa
Mostrar:
- score atual
- decomposição
- histórico
- resumo
- riscos

### Comparador
Comparar 2 a 5 ativos.

### Monitor
Mostrar:
- entradas e saídas
- alertas
- maiores altas e quedas

## 21. Dashboards

### Visão executiva
- top 20
- top por tese
- mudanças do mês

### Visão analista
- score completo
- decomposição
- benchmarks
- histórico
- flags

## 22. Segurança e governança

### Autenticação
Implementar depois do MVP:
- login
- papéis
- sessão

### Papéis
- admin
- analista
- viewer

### Auditoria
Registrar:
- data
- job
- status
- origem
- versão do modelo

### Versionamento do modelo
Guardar:
- versão das configs setoriais
- versão do scoring engine
- data do snapshot

## 23. Observabilidade

### Logs
Precisam existir para:
- ingestão
- enriquecimento
- score
- ranking
- API
- jobs

### Métricas úteis
- tempo de pipeline
- falhas por provider
- empresas processadas
- ativos elegíveis
- ativos descartados

## 24. Roadmap de implementação

### Fase 1 — MVP técnico
- ambiente
- banco
- migrations
- CRUD básico
- API mínima

### Fase 2 — Dados reais
- ingestão CVM
- ingestão B3
- persistência

### Fase 3 — Mercado e score
- valuation atual
- benchmarks
- score
- ranking

### Fase 4 — Produto usável
- dashboard
- screener
- detalhe da ação
- monitor

### Fase 5 — Agent layer
- top 20 comentado
- briefing
- explicação de mudanças

### Fase 6 — Produto escalável
- autenticação
- watchlists
- alertas multicanal
- billing

## 25. Ordem obrigatória de build

1. dados
2. score
3. ranking
4. API
5. dashboard
6. agente

## 26. Checklist resumido

### Ambiente
- [ ] Docker sobe
- [ ] backend responde
- [ ] frontend abre
- [ ] banco conecta
- [ ] Redis conecta

### Banco
- [ ] Alembic configurado
- [ ] schema criado
- [ ] seed de setores

### API
- [ ] /companies
- [ ] /companies/{ticker}
- [ ] /scores/{ticker}
- [ ] /rankings/top20

### Dados
- [ ] ingestão CVM
- [ ] ingestão B3
- [ ] persistência idempotente

### Mercado
- [ ] preço
- [ ] múltiplos
- [ ] benchmarks

### Score
- [ ] blocos brutos
- [ ] ponderação
- [ ] penalties
- [ ] bucket
- [ ] classe

### Ranking
- [ ] top 20
- [ ] rankings por setor
- [ ] snapshots
- [ ] comparação temporal

### Frontend
- [ ] home
- [ ] screener
- [ ] detalhe da empresa
- [ ] comparação
- [ ] monitor

### Automação
- [ ] jobs
- [ ] logs
- [ ] alertas

### IA
- [ ] resumo de tese
- [ ] explicação de mudanças
- [ ] top 20 comentado

## 27. Critérios de aceite do MVP

O MVP é aceito quando:
- backend sobe
- banco está migrado
- ingestão funciona
- score é calculado para conjunto de teste
- top 20 sai por API
- frontend exibe ranking e detalhe
- snapshots ficam armazenados
- agente está separado do motor oficial

## 28. Erros que não devem acontecer

- calcular score no frontend
- usar agente como motor do score
- sobrescrever histórico
- comparar setores errados
- quebrar pipeline inteiro por dado opcional ausente
- começar pelo dashboard bonito
- construir tudo em planilha

## 29. Instrução final ao programador

A ordem correta é:

**dados primeiro, score depois, ranking depois, dashboard depois, agente por último.**

Essa ordem é obrigatória.
