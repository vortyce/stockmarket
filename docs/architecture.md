# Arquitetura

## Visão geral
O sistema é composto por:
- Pipeline de ingestão de dados (CVM, B3 e fonte complementar de mercado)
- Banco PostgreSQL para dados estruturados
- Backend FastAPI para APIs e orquestração
- Frontend Next.js para dashboards e screener
- Jobs Python para recálculo e geração de rankings

## Componentes
- `companies`: cadastro de empresas
- `financials_annual`: históricos anuais
- `market_snapshots`: métricas atuais de mercado
- `trend_snapshots`: sinais de tendência
- `risk_flags`: penalizações
- `sector_configs`: pesos por setor
- `score_snapshots`: score consolidado
- `ranking_snapshots`: rankings gerados

## Fluxo
1. Ingestão de dados brutos
2. Consolidação de métricas
3. Aplicação do modelo de score
4. Geração de rankings
5. Exposição por API
6. Visualização em dashboard
