# StockMarket — Release README

## Status da release

Esta release representa o estado atual consolidado do projeto **StockMarket**, já sincronizado com o repositório remoto oficial.

Repositório:
`https://github.com/vortyce/stockmarket`

Branch principal:
`main`

Estado:
**sincronizado entre local e remoto**

---

## Visão geral

O projeto é um sistema multi-camadas para análise de ações da bolsa, combinando:

- **Screener Base**
- **Ranking Upside 12M**
- **Módulo de Opções**

A proposta central é separar claramente três motores analíticos:

### 1. Screener Base
Motor quantitativo principal para filtrar ativos com base em:

- universo investível
- qualidade mínima
- valuation
- dividendos
- robustez operacional
- buckets interpretáveis

### 2. Upside 12M
Motor secundário e independente focado em:

- potencial de valorização em 12 meses
- re-rating
- recuperação operacional
- assimetria
- sinais de armadilha de upside

### 3. Módulo de Opções
Overlay operacional para geração e monitoramento de:

- **Covered Calls**
- **Cash-Secured Puts**

incluindo:
- sugestões táticas
- monitoramento de posições
- sinais de saída
- bloqueio/liberação de rolagem por tese

---

## O que está implementado nesta release

## Backend

- API em FastAPI
- banco com PostgreSQL
- migrations com Alembic
- arquitetura com repositories e services
- jobs de ingestão e recálculo
- versionamento de snapshots
- logs operacionais
- suporte a monitoramento tático de opções

## Frontend

- interface em Next.js + TypeScript
- Dashboard principal
- Ranking Base
- Screener
- Detalhe de empresa
- Ranking Upside 12M
- Painel de Opções
- Monitoramento de posições
- Sugestões de operações

## Dados e pipelines

- ingestão estrutural de empresas
- ingestão contábil via CVM
- ingestão de mercado
- snapshots de score e ranking
- snapshots de opções
- refresh completo por job único

---

## Módulos da release

## 1. Screener Base

### Objetivo
Selecionar ações com melhor combinação de:
- qualidade
- valuation
- renda
- robustez

### Saídas
- score final
- rating
- bucket
- ranking top 20
- detalhe por ticker

---

## 2. Upside 12M

### Objetivo
Identificar ativos com maior potencial de valorização em médio prazo.

### Blocos do score
- Upside Externo
- Re-rating Potencial
- Recuperação Operacional
- Assimetria
- Governança/Liquidez

### Buckets
- Armadilha de Upside
- Assimetria Atrativa
- Recuperação Operacional
- Re-rating Forte
- Upside de Research
- Neutro

### Observações
- módulo separado do Screener Base
- snapshots próprios
- endpoints próprios
- frontend próprio

---

## 3. Módulo de Opções

### Estratégias suportadas
- Covered Call
- Cash-Secured Put

### Funcionalidades implementadas
- policy configurável
- ingestão de option chains
- sugestões por ativo
- regra best-only por estratégia
- monitoramento tático
- EXIT_TIME
- EXIT_PROFIT
- bloqueio de roll por tese
- painel visual dedicado

### Observações
- o módulo de opções é um **overlay**
- não altera o score oficial das ações
- depende da carteira e do caixa para elegibilidade real

---

## Jobs principais

### Refresh completo
```bash
python -m app.jobs.full_refresh
```

### Recalcular Upside 12M
```bash
python -m app.jobs.recalculate_upside12m
```

### Atualizar cadeias de opções
```bash
python -m app.jobs.update_option_chains
```

### Gerar sugestões de opções
```bash
python -m app.jobs.generate_options_suggestions
```

### Monitorar saídas de opções
```bash
python -m app.jobs.monitor_option_exits
```

---

## URLs principais

### Frontend
- `/`
- `/screener`
- `/upside`
- `/options`

### Backend
- `/health`
- `/api/v1/companies`
- `/api/v1/rankings/top20`
- `/api/v1/upside12m/top20`
- `/api/v1/options/suggestions`
- `/api/v1/options/monitor`

---

## Estado atual do projeto

Esta release pode ser considerada um **MVP funcional consolidado**.

Ela já entrega:

- análise base de ações
- ranking alternativo de upside
- painel tático de opções
- sincronização local/remoto validada
- documentação consolidada

---

## Limitações conhecidas

- provider de mercado ainda pode depender de fonte provisória em alguns fluxos
- parte dos dados externos pode variar conforme disponibilidade da fonte
- rerating do módulo Upside 12M melhora com mais histórico de snapshots
- o módulo de opções ainda pode evoluir em payoff, execução e integração com corretora

---

## Próximas evoluções sugeridas

- release/tag formal no GitHub
- changelog versionado
- provider de mercado mais robusto
- payoff diagrams
- exportação de ordens
- integração com OMS/corretora
- enriquecimento de research targets
- monitor de carteira e alocação

---

## Situação de sincronização

Estado verificado:
- local e remoto sincronizados
- branch `main`
- nenhum commit pendente
- nenhum diff entre `main` e `origin/main`

---

## Resumo final

Esta release representa a primeira versão coesa do sistema com:

- **Screener Base**
- **Upside 12M**
- **Opções**

O projeto já está em condição de:
- demonstração
- auditoria
- continuidade de desenvolvimento
- handoff técnico
