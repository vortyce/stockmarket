# B3 Screener

Sistema de triagem quantitativa para ações da bolsa brasileira.

## Objetivo

O B3 Screener não é um robô comprador.  
Ele é um motor de triagem para:

- ingerir dados contábeis e de mercado
- consolidar métricas por empresa
- calcular score por setor
- gerar rankings e buckets
- expor APIs
- exibir dashboards
- usar IA apenas para explicação e automação auxiliar

## Stack proposta

### Backend
- Python
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Redis

### Frontend
- Next.js
- TypeScript

### Infra
- Docker
- Docker Compose

## Estrutura

```text
backend/
frontend/
infra/
docs/
```

## Ordem correta de implementação

1. dados
2. score
3. ranking
4. API
5. dashboard
6. agente

## Módulos principais

- ingestão CVM
- ingestão B3
- enriquecimento de mercado
- benchmark setorial
- scoring engine (Screener Base)
- ranking engine (Screener Base)
- **Upside 12M Module (Alpha)**: Motor quantitativo independente para potencial de valorização.
- API REST
- dashboards
- camada agentic auxiliar

## Endpoints mínimos

- `GET /health`
- `GET /companies`
- `GET /companies/{ticker}`
- `GET /scores/{ticker}`
- `GET /rankings/top20`
- `POST /jobs/ingest`
- `POST /jobs/recalculate`

## Documentação

- `docs/B3_Screener_PRD_Tecnico.md`
- `docs/IMPLEMENTATION_CHECKLIST.md`
- `docs/API_CONTRACT.md`

## Regra central

O score oficial deve ser:

- determinístico
- auditável
- reproduzível

Agentes não podem alterar o score oficial.
