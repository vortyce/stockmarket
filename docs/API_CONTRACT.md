# API Contract

## Base URL

```text
/api/v1
```

## Authentication

No MVP, autenticação pode ficar desativada para ambiente interno.  
Em produção, implementar autenticação e controle de acesso.

---

## Health

### `GET /health`

Retorna status da aplicação.

### Response
```json
{
  "status": "ok"
}
```

---

## Companies

### `GET /companies`

Lista empresas.

### Query params
- `sector` (opcional): filtra por setor

### Example
```http
GET /companies?sector=BANCOS
```

### Response
```json
[
  {
    "id": "uuid",
    "ticker": "BBAS3",
    "company_name": "BANCO DO BRASIL",
    "sector": "BANCOS",
    "subsector": "BANCOS",
    "listing_segment": "NOVO MERCADO",
    "main_index": "IBOV",
    "free_float": 0.47,
    "avg_daily_liquidity": 120000000
  }
]
```

### `GET /companies/{ticker}`

Retorna uma empresa por ticker.

### Example
```http
GET /companies/BBAS3
```

### Success response
```json
{
  "id": "uuid",
  "ticker": "BBAS3",
  "company_name": "BANCO DO BRASIL",
  "sector": "BANCOS",
  "subsector": "BANCOS",
  "listing_segment": "NOVO MERCADO",
  "main_index": "IBOV",
  "free_float": 0.47,
  "avg_daily_liquidity": 120000000
}
```

### Not found
```json
{
  "detail": "Ticker não encontrado"
}
```

---

## Scores

### `GET /scores/{ticker}`

Retorna o score mais recente de um ticker.

### Example
```http
GET /scores/BBAS3
```

### Response
```json
{
  "ticker": "BBAS3",
  "company_name": "BANCO DO BRASIL",
  "as_of_date": "2026-04-21",
  "sector": "BANCOS",
  "quality_raw": 24,
  "valuation_raw": 21,
  "dividends_raw": 8,
  "trend_raw": 13,
  "gov_liq_raw": 9,
  "quality_weighted": 28.0,
  "valuation_weighted": 17.5,
  "dividends_weighted": 12.0,
  "trend_weighted": 9.75,
  "gov_liq_weighted": 9.0,
  "penalty": 2,
  "final_score": 74.25,
  "rating_class": "Monitorar",
  "bucket": "Financeiro Defensivo",
  "summary": "Ticker com qualidade sólida e valuation relativamente atrativo."
}
```

### Not found
```json
{
  "detail": "Score não encontrado"
}
```

---

## Rankings

### `GET /rankings/top20`

Retorna top 20 do ranking geral.

### Query params
- `scope` (opcional, default=`general`)
- `as_of_date` (opcional, formato `YYYY-MM-DD`)

### Example
```http
GET /rankings/top20?scope=general&as_of_date=2026-04-21
```

### Response
```json
[
  {
    "position": 1,
    "ticker": "BBAS3",
    "company_name": "BANCO DO BRASIL",
    "sector": "BANCOS",
    "final_score": 74.25,
    "bucket": "Financeiro Defensivo",
    "rating_class": "Monitorar"
  }
]
```

### `GET /rankings/by-sector`

Retorna ranking filtrado por setor.

### Query params
- `sector` (obrigatório)
- `limit` (opcional, default=20)
- `as_of_date` (opcional)

### Example
```http
GET /rankings/by-sector?sector=ELÉTRICAS&limit=10
```

### Response
```json
[
  {
    "position": 1,
    "ticker": "EGIE3",
    "company_name": "ENGIE BRASIL",
    "sector": "ELÉTRICAS",
    "final_score": 71.4,
    "bucket": "Renda Defensiva",
    "rating_class": "Monitorar"
  }
]
```

### `GET /rankings/history`

Retorna histórico de score/ranking de um ticker.

### Query params
- `ticker` (obrigatório)

### Example
```http
GET /rankings/history?ticker=BBAS3
```

### Response
```json
[
  {
    "as_of_date": "2026-01-31",
    "final_score": 70.1,
    "position": 5,
    "bucket": "Financeiro Defensivo"
  },
  {
    "as_of_date": "2026-02-28",
    "final_score": 72.3,
    "position": 3,
    "bucket": "Financeiro Defensivo"
  }
]
```

---

## Jobs

### `POST /jobs/ingest`

Dispara ingestão de dados.

### Response
```json
{
  "status": "queued",
  "job": "ingest"
}
```

### `POST /jobs/recalculate`

Dispara recálculo do scoring e do ranking.

### Response
```json
{
  "status": "queued",
  "job": "recalculate_scores"
}
```

---

## Alerts

### `GET /alerts`

Lista alertas ativos.

### Response
```json
[
  {
    "type": "entered_top20",
    "ticker": "TAEE11",
    "as_of_date": "2026-04-21",
    "message": "Ticker entrou no top 20 geral."
  },
  {
    "type": "bucket_changed",
    "ticker": "PETR4",
    "as_of_date": "2026-04-21",
    "message": "Ticker mudou para bucket Cíclica Descontada."
  }
]
```

---

## Error format

### Default error
```json
{
  "detail": "Mensagem de erro"
}
```

---

## Notes

- O score oficial é calculado no backend.
- O frontend não deve recalcular score.
- A camada de IA pode comentar resultados, mas não alterar o score oficial.
