# Módulo Upside 12M

Este módulo é um motor quantitativo secundário e independente do Screener Base. Seu objetivo é identificar ativos com maior potencial de valorização em um horizonte de 12 meses, ponderando alvos externos (research), descontos históricos (re-rating) e sinais de recuperação operacional.

## 🏗️ Arquitetura
- **Desacoplamento**: Opera em tabelas próprias e não interfere no cálculo do Score de Qualidade (Screener Base).
- **Snapshot Diário**: Persiste um registro por ticker por dia em `upside_12m_snapshots`.
- **Ranking Votado**: Gera um Top 20 diário em `upside_12m_rankings`.

## 🧮 Engine de Scoring (v1.2)
O score final é calculado com base em 5 blocos principais:

| Bloco | Peso | Critério de Cálculo |
|---|---|---|
| **Upside Externo** | 30% | Potencial teórico (Target Research / Preço Capturado). |
| **Re-rating Potencial** | 25% | Desconto do P/L e P/VP atual vs. média histórica do ativo. |
| **Recuperação Operacional** | 25% | Tendência de crescimento de EBITDA e expansão de margens YoY. |
| **Assimetria** | 10% | Valuation deprimido + Margens em alta + Dívida estável. |
| **Gov/Liquidez** | 10% | Segmento Novo Mercado + Free Float > 25%. |

### Penalidades (Redutores de Score)
- **Queda de Lucro**: -30 a -50 pontos se lucro líquido cair > 50% ou prejuízo aumentar.
- **Endividamento**: -40 pontos se Dívida/EBITDA > 4.0 (Isenção aplicada a bancos/financeiras).

## 📊 Buckets e Ratings
O motor classifica os ativos em buckets de tese por ordem de precedência técnica:
1. **Armadilha de Upside**: Upside teórico alto mas fundamentos em deterioração (Risco de Value Trap).
2. **Assimetria Atrativa**: Combinação de desconto profundo e melhora operacional.
3. **Recuperação Operacional**: Foco em turn-around ou ganho de eficiência.
4. **Re-rating Forte**: Foco em desconto histórico de múltiplos.
5. **Upside de Research**: Baseado principalmente no consenso de mercado.
6. **Neutro**: Sem drivers claros identificados.

## 🛠️ Operacional
- **Job de Recálculo**: `python -m app.jobs.recalculate_upside12m` (Pode ser disparado via API).
- **Provider**: Yahoo Finance (através de `yfinance`).
- **Data Source Contábil**: CVM (DFP/ITR).

## 🚀 Endpoints de API
- `GET /api/v1/upside12m/top20`: Retorna a fotografia do ranking diário.
- `GET /api/v1/upside12m/{ticker}`: Detalhamento completo do score e tese.
- `GET /api/v1/upside12m/history`: Histórico de evolução do score.
- `POST /api/v1/upside12m/jobs/recalculate`: Dispara o job de recálculo manual.

## ⚠️ Limitações Conhecidas
- **Histórico Re-rating**: O cálculo de desconto histórico depende do número de snapshots armazenados. No início, o score tende a 50 (neutro) por falta de base comparativa.
- **Setores Financeiros**: Penalidades de margem EBITDA são menos precisas para bancos devido à estrutura de receita de juros.
- **Provider Provisório**: O Yahoo Finance pode sofrer com instabilidades ou limites de taxa (Rate Limit).
