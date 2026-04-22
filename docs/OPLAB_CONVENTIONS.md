# OpLab API Conventions (v3)

Baseado em testes realizados em 21/04/2026.

## 1. Tickers e Símbolos
- **Ativo Objeto (Underlying)**: Usa o ticker padrão sem sufixos (ex: `PETR4`, `BBAS3`).
- **Opções**: Usa o símbolo B3 de 10 caracteres (ex: `PETRD319W4`).
- **Cadeia de Opções**: Obtida via `GET /market/options/{underlying}`.

## 2. Estrutura da Resposta de Opções
| Campo | Descrição | Exemplo |
| :--- | :--- | :--- |
| `symbol` | Símbolo B3 da opção | `PETRD319W4` |
| `category` / `type` | Tipo da opção | `CALL` / `PUT` |
| `due_date` | Data de vencimento | `2026-04-24` |
| `days_to_maturity` | DTE (Days to Expiration) | `2` |
| `strike` | Preço de exercício | `31.9` |
| `spot_price` | Preço do ativo objeto | `47.02` |
| `bid` / `ask` | Preço de compra/venda | `0.62` / `0.65` |
| `close` | Último preço negociado | `16.7` |

## 3. Gregos e Volatilidade (Black-Scholes)
- **Status**: Não disponíveis no endpoint de listagem de massa (`/market/options/{ticker}`).
- **Conformidade**: Implementaremos um motor Black-Scholes local (`GreeksCalculator`) no backend para garantir a disponibilidade de Delta, Theta e IV para o motor de sugestões.
- **Input p/ Cálculo**:
  - Preço da Opção (Mid ou Close)
  - Preço do Ativo (Spot)
  - Strike
  - Tempo até o vencimento (DTE / 365)
  - Taxa livre de risco (Selic ~10.75% a.a.)

## 4. Idempotência de Snapshots
- **Snapshots de Cadeia**: Identificados de forma única por `(ticker, option_symbol, snapshot_at)`.
- **Estratégia de Limpeza**: Manter apenas snapshots do dia atual para consulta ativa; snapshots históricos serão arquivados para auditoria futura.
