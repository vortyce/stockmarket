# OPTIONS_IMPLEMENTATION_CHECKLIST

## Fase 1 — Banco

- [ ] Criar migration para `portfolio_positions`
- [ ] Criar migration para `portfolio_cash`
- [ ] Criar migration para `option_chain_snapshots`
- [ ] Criar migration para `options_policy_configs`
- [ ] Criar migration para `options_suggestions`
- [ ] Criar migration para `options_positions`
- [ ] Criar migration para `options_roll_actions`
- [ ] Criar seed da política default

## Fase 2 — Models e Schemas

- [ ] Criar model `PortfolioPosition`
- [ ] Criar model `PortfolioCash`
- [ ] Criar model `OptionChainSnapshot`
- [ ] Criar model `OptionsPolicyConfig`
- [ ] Criar model `OptionsSuggestion`
- [ ] Criar model `OptionsPosition`
- [ ] Criar model `OptionsRollAction`

- [ ] Criar schemas de carteira
- [ ] Criar schemas de política
- [ ] Criar schemas de sugestão
- [ ] Criar schemas de monitoramento

## Fase 3 — Dados de carteira

- [ ] Implementar `GET /portfolio`
- [ ] Implementar `POST /portfolio/positions`
- [ ] Implementar `PATCH /portfolio/positions/{id}`
- [ ] Implementar `GET /portfolio/cash`
- [ ] Implementar `PATCH /portfolio/cash`

## Fase 4 — Cadeia de opções

- [ ] Definir provider de cadeia de opções
- [ ] Implementar ingestão de option chain
- [ ] Persistir snapshots
- [ ] Garantir atualização idempotente
- [ ] Registrar logs de provider

## Fase 5 — Política operacional

- [ ] Implementar leitura da política ativa
- [ ] Implementar `GET /options/policy`
- [ ] Implementar `PATCH /options/policy`
- [ ] Garantir configuração por usuário ou default global

## Fase 6 — Suggestion engine

### Covered Call
- [ ] Verificar posição em carteira
- [ ] Verificar lote coberto
- [ ] Verificar posição núcleo
- [ ] Verificar bucket proibido
- [ ] Filtrar delta
- [ ] Filtrar DTE
- [ ] Filtrar liquidez
- [ ] Gerar top sugestões

### Cash-Secured Put
- [ ] Verificar score mínimo
- [ ] Verificar bucket proibido
- [ ] Verificar caixa suficiente
- [ ] Filtrar delta
- [ ] Filtrar DTE
- [ ] Filtrar liquidez
- [ ] Calcular preço efetivo de entrada
- [ ] Gerar top sugestões

### Persistência
- [ ] Persistir sugestões em `options_suggestions`
- [ ] Expor `GET /options/suggestions`
- [ ] Expor endpoints filtrados por tipo

## Fase 7 — Posições aceitas

- [ ] Implementar `POST /options/positions`
- [ ] Implementar `GET /options/positions`
- [ ] Calcular `exit_target_price`
- [ ] Persistir status da operação

## Fase 8 — Monitor de saída

- [ ] Atualizar preço atual da opção
- [ ] Calcular lucro %
- [ ] Calcular DTE atual
- [ ] Verificar gatilho de 50%
- [ ] Verificar gatilho de 21 DTE
- [ ] Expor `GET /options/monitor`

## Fase 9 — Sugestões de rolagem

- [ ] Implementar regra de rolagem de put
- [ ] Implementar regra de rolagem de call
- [ ] Expor `GET /options/roll-suggestions`
- [ ] Persistir ações em `options_roll_actions`

## Fase 10 — Jobs

- [ ] Criar job `update_option_chains`
- [ ] Criar job `generate_option_suggestions`
- [ ] Criar job `monitor_option_exits`
- [ ] Expor jobs por API

## Fase 11 — Frontend

### Carteira
- [ ] Tela `/portfolio`
- [ ] Tabela de posições
- [ ] Caixa disponível
- [ ] Flags de covered call

### Sugestões
- [ ] Tela `/options`
- [ ] Tabela de covered calls
- [ ] Tabela de cash-secured puts
- [ ] Filtros por status

### Detalhe
- [ ] Tela `/options/suggestions/[id]`
- [ ] Motivo da sugestão
- [ ] Risco principal
- [ ] Regra de saída
- [ ] Overlay score

### Monitor
- [ ] Tela de operações abertas
- [ ] Lucro %
- [ ] DTE
- [ ] Fechar / rolar / manter

## Fase 12 — Testes

### Unitários
- [ ] Teste de filtro de covered call
- [ ] Teste de filtro de cash-secured put
- [ ] Teste de cálculo de spread %
- [ ] Teste de cálculo de capital requerido
- [ ] Teste de gatilho de 50%
- [ ] Teste de gatilho de 21 DTE
- [ ] Teste de sugestão de rolagem

### Integração
- [ ] API de carteira
- [ ] API de sugestões
- [ ] API de monitor
- [ ] Jobs de opções

## Critérios de aceite

- [ ] Módulo lê carteira e caixa
- [ ] Módulo lê cadeia de opções
- [ ] Política operacional é configurável
- [ ] Sugestões de covered call funcionam
- [ ] Sugestões de cash-secured put funcionam
- [ ] Monitor de saída funciona
- [ ] Sugestões de rolagem funcionam
- [ ] Overlay não altera score oficial das ações
