# OPTIONS_API_CONTRACT

## Base URL

```text
/api/v1
```

## Portfolio

### `GET /portfolio`
Lista posições da carteira.

### Response
```json
[
  {
    "id": "uuid",
    "ticker": "BBAS3",
    "quantity": 200,
    "avg_price": 27.5,
    "current_weight": 0.08,
    "thesis_type": "renda",
    "is_core_position": false,
    "allow_covered_call": true
  }
]
```

### `POST /portfolio/positions`
Cria posição na carteira.

### Request
```json
{
  "ticker": "BBAS3",
  "quantity": 200,
  "avg_price": 27.5,
  "current_weight": 0.08,
  "thesis_type": "renda",
  "is_core_position": false,
  "allow_covered_call": true
}
```

### Response
```json
{
  "status": "created"
}
```

### `PATCH /portfolio/positions/{id}`
Atualiza uma posição.

### `GET /portfolio/cash`
Retorna caixa disponível.

### Response
```json
{
  "available_cash": 50000,
  "reserved_cash_for_puts": 12000
}
```

### `PATCH /portfolio/cash`
Atualiza caixa.

### Request
```json
{
  "available_cash": 50000,
  "reserved_cash_for_puts": 12000
}
```

---

## Option Chains

### `GET /options/chains/{ticker}`
Retorna a cadeia de opções mais recente do ativo.

### Example
```http
GET /options/chains/BBAS3
```

### Response
```json
{
  "ticker": "BBAS3",
  "snapshot_at": "2026-04-21T15:30:00Z",
  "items": [
    {
      "option_symbol": "BBAS3C300",
      "option_type": "CALL",
      "expiration_date": "2026-05-21",
      "dte": 30,
      "strike": 30.0,
      "bid": 0.62,
      "ask": 0.68,
      "mid_price": 0.65,
      "volume": 1500,
      "open_interest": 5200,
      "implied_volatility": 0.27,
      "delta": 0.19,
      "theta": -0.03,
      "gamma": 0.02,
      "underlying_price": 28.4
    }
  ]
}
```

---

## Policy

### `GET /options/policy`
Retorna a política operacional ativa.

### Response
```json
{
  "policy_name": "DEFAULT_OPTIONS_POLICY",
  "min_dte": 30,
  "max_dte": 45,
  "exit_dte": 21,
  "profit_target_pct": 0.5,
  "covered_call_delta_min": 0.15,
  "covered_call_delta_max": 0.25,
  "cash_put_delta_min": 0.15,
  "cash_put_delta_max": 0.25,
  "min_open_interest": 300,
  "min_bid": 0.15,
  "max_spread_pct": 0.2,
  "allow_calls_on_deep_value": false,
  "allow_puts_on_rerating": false
}
```

### `PATCH /options/policy`
Atualiza a política operacional.

### Request
```json
{
  "min_dte": 30,
  "max_dte": 45,
  "exit_dte": 21,
  "profit_target_pct": 0.5,
  "covered_call_delta_min": 0.15,
  "covered_call_delta_max": 0.25
}
```

---

## Suggestions

### `GET /options/suggestions`
Lista sugestões de opções.

### Query params
- `suggestion_type` (opcional): `COVERED_CALL` ou `CASH_SECURED_PUT`
- `status` (opcional): `OPEN`, `ACCEPTED`, `IGNORED`, `EXPIRED`

### Response
```json
[
  {
    "id": "uuid",
    "ticker": "BBAS3",
    "suggestion_type": "COVERED_CALL",
    "expiration_date": "2026-05-21",
    "dte": 30,
    "strike": 30.0,
    "premium": 0.65,
    "delta": 0.19,
    "open_interest": 5200,
    "contracts": 2,
    "capital_required": null,
    "effective_entry_price": null,
    "expected_income": 130.0,
    "overlay_score": 78.4,
    "reason_summary": "Ação em carteira com perfil mais maduro para monetização via call coberta.",
    "risk_summary": "Pode limitar upside se a ação disparar.",
    "exit_rule_summary": "Sair em 21 DTE ou com 50% do lucro."
  }
]
```

### `GET /options/suggestions/covered-calls`
Lista apenas sugestões de covered call.

### `GET /options/suggestions/cash-puts`
Lista apenas sugestões de cash-secured put.

---

## Accepted positions

### `GET /options/positions`
Lista operações aceitas/executadas.

### Response
```json
[
  {
    "id": "uuid",
    "ticker": "BBAS3",
    "option_symbol": "BBAS3C300",
    "option_type": "CALL",
    "contracts": 2,
    "strike": 30.0,
    "expiration_date": "2026-05-21",
    "entry_price": 0.65,
    "current_price": 0.31,
    "entry_date": "2026-04-21",
    "status": "OPEN",
    "exit_target_price": 0.325,
    "exit_dte_rule": 21,
    "profit_target_pct": 0.5
  }
]
```

### `POST /options/positions`
Marca sugestão como executada ou cria posição manualmente.

### Request
```json
{
  "suggestion_id": "uuid",
  "entry_price": 0.65,
  "entry_date": "2026-04-21"
}
```

### Response
```json
{
  "status": "created"
}
```

---

## Monitoring

### `GET /options/monitor`
Retorna monitoramento das posições abertas.

### Response
```json
[
  {
    "position_id": "uuid",
    "ticker": "BBAS3",
    "option_symbol": "BBAS3C300",
    "current_profit_pct": 0.52,
    "current_dte": 20,
    "should_close": true,
    "close_reason": "Atingiu meta de lucro."
  }
]
```

---

## Rolls

### `GET /options/roll-suggestions`
Lista sugestões de rolagem.

### Response
```json
[
  {
    "position_id": "uuid",
    "ticker": "BBAS3",
    "option_symbol": "BBAS3C300",
    "action_type": "ROLL_UP",
    "reason": "Call ameaça exercício e ação deve ser mantida; considerar rolagem."
  }
]
```

---

## Jobs

### `POST /jobs/update-option-chains`
Dispara atualização das cadeias de opções.

### Response
```json
{
  "status": "queued",
  "job": "update_option_chains"
}
```

### `POST /jobs/generate-option-suggestions`
Dispara geração de sugestões.

### Response
```json
{
  "status": "queued",
  "job": "generate_option_suggestions"
}
```

### `POST /jobs/monitor-option-exits`
Dispara monitoramento de saída e rolagem.

### Response
```json
{
  "status": "queued",
  "job": "monitor_option_exits"
}
```

## Notes

- O módulo de opções usa o score da ação como insumo, mas não altera o score oficial.
- A política operacional deve ser configurável.
- O frontend não recalcula a lógica do overlay; apenas exibe a decisão do backend.
