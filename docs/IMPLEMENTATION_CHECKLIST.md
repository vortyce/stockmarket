# Implementation Checklist

## Fase 0 — Ambiente

- [ ] Clonar o repositório
- [ ] Configurar variáveis de ambiente
- [ ] Subir Docker Compose
- [ ] Validar PostgreSQL
- [ ] Validar Redis
- [ ] Validar backend em `/health`
- [ ] Validar frontend local

## Fase 1 — Banco e migrations

- [ ] Configurar Alembic
- [ ] Criar migrations iniciais
- [ ] Criar tabelas:
  - [ ] companies
  - [ ] financials_annual
  - [ ] market_snapshots
  - [ ] trend_snapshots
  - [ ] risk_flags
  - [ ] sector_configs
  - [ ] score_snapshots
  - [ ] ranking_snapshots
- [ ] Rodar `alembic upgrade head`
- [ ] Criar seed de `sector_configs`

## Fase 2 — API mínima

- [ ] Implementar `GET /companies`
- [ ] Implementar `GET /companies/{ticker}`
- [ ] Implementar `GET /scores/{ticker}`
- [ ] Implementar `GET /rankings/top20`
- [ ] Criar schemas Pydantic
- [ ] Criar repositories
- [ ] Testar respostas com dados mockados

## Fase 3 — Ingestão de dados

- [ ] Implementar ingestão CVM
- [ ] Implementar ingestão B3
- [ ] Garantir idempotência
- [ ] Registrar logs de pipeline
- [ ] Persistir dados em `financials_annual`
- [ ] Persistir cadastro em `companies`

## Fase 4 — Mercado

- [ ] Implementar provider de preço e múltiplos
- [ ] Popular `market_snapshots`
- [ ] Calcular Graham Number
- [ ] Calcular valor justo simples
- [ ] Calcular descontos
- [ ] Tratar faltas de dados sem quebrar pipeline

## Fase 5 — Benchmark setorial

- [ ] Calcular média setorial de P/L
- [ ] Calcular média setorial de P/VP
- [ ] Calcular média setorial de EV/EBITDA
- [ ] Persistir benchmark setorial

## Fase 6 — Scoring engine

- [ ] Implementar score de qualidade
- [ ] Implementar score de valuation
- [ ] Implementar score de dividendos
- [ ] Implementar score de tendência
- [ ] Implementar score de governança/liquidez
- [ ] Implementar penalties
- [ ] Implementar pesos por setor
- [ ] Persistir `score_snapshots`

## Fase 7 — Ranking engine

- [ ] Gerar top 20 geral
- [ ] Gerar ranking por setor
- [ ] Gerar ranking por bucket
- [ ] Gerar listas de value traps
- [ ] Persistir `ranking_snapshots`
- [ ] Comparar snapshot atual vs anterior

## Fase 8 — Jobs

- [ ] Criar job de ingestão
- [ ] Criar job de enriquecimento
- [ ] Criar job de recálculo
- [ ] Criar job de ranking
- [ ] Expor `POST /jobs/ingest`
- [ ] Expor `POST /jobs/recalculate`
- [ ] Registrar status dos jobs

## Fase 9 — Frontend

- [ ] Dashboard home
- [ ] Screener com filtros
- [ ] Página de detalhe da empresa
- [ ] Página de comparação
- [ ] Página de monitor
- [ ] Integrar com API

## Fase 10 — Alertas

- [ ] Alertar entrada no top 20
- [ ] Alertar saída do top 20
- [ ] Alertar mudança de bucket
- [ ] Alertar piora de score
- [ ] Exibir alertas no dashboard

## Fase 11 — IA auxiliar

- [ ] Gerar resumo de tese
- [ ] Explicar mudança de score
- [ ] Criar top 20 comentado
- [ ] Manter agente separado do motor oficial

## Testes obrigatórios

- [ ] Testes unitários do scoring
- [ ] Testes de integração da API
- [ ] Testes do pipeline de ingestão
- [ ] Testes por setor:
  - [ ] banco
  - [ ] seguradora
  - [ ] elétrica
  - [ ] commodity
  - [ ] varejo
  - [ ] industrial
  - [ ] holding

## Critérios de aceite do MVP

- [ ] Stack sobe sem erro
- [ ] Banco migrado
- [ ] Ingestão funcional
- [ ] Score calculado para conjunto de teste
- [ ] Top 20 disponível por API
- [ ] Frontend exibindo ranking
- [ ] Snapshots armazenados
- [ ] IA separada do score oficial
