# Contrato de API

## Endpoints principais
- `GET /health`
- `GET /companies`
- `GET /companies/{ticker}`
- `GET /scores/{ticker}`
- `GET /rankings/top20`
- `POST /jobs/recalculate`

## Exemplo de resposta `GET /rankings/top20`
```json
[
  {
    "position": 1,
    "ticker": "BBAS3",
    "company_name": "Banco do Brasil",
    "sector": "BANCOS",
    "final_score": 82.5,
    "bucket": "Financeiro Defensivo",
    "rating_class": "Muito Boa"
  }
]
```
