# OPTIONS_OVERLAY_PRD

## 1. Objetivo

Adicionar ao sistema B3 Screener um módulo de overlay de opções para sugerir:

- venda de **covered calls** sobre ações já presentes na carteira
- venda de **cash-secured puts** sobre ações elegíveis do universo
- monitoramento de operações aceitas
- monitoramento de regras de saída e rolagem

## 2. Princípio central

O módulo de opções **não substitui** o motor principal de ações.

O fluxo correto é:

1. o screener escolhe boas ações
2. o overlay de opções avalia se existe operação de prêmio compatível
3. o sistema sugere a operação
4. o usuário decide executar ou não

## 3. Estratégias suportadas no MVP

### 3.1 Covered Call
Venda de call coberta por ações já presentes na carteira.

### 3.2 Cash-Secured Put
Venda de put com caixa integralmente reservado para eventual exercício.

## 4. Estratégias fora do MVP

Não implementar no MVP:
- naked call
- put descoberta
- strangle
- straddle
- iron condor
- ratio spread
- calendar spread
- diagonais
- sintéticas complexas

## 5. Regras operacionais do MVP

### Covered Call
- DTE entre 30 e 45
- delta entre 0,15 e 0,25
- saída em 21 DTE ou 50% do lucro, o que vier primeiro
- somente se houver lote coberto suficiente
- evitar em ações muito descontadas ou em forte rerating

### Cash-Secured Put
- DTE entre 35 e 45
- delta entre 0,15 e 0,25
- saída em 21 DTE ou 50% do lucro, o que vier primeiro
- somente com caixa integral disponível
- somente em ações que o usuário aceitaria comprar no strike

## 6. Critérios mínimos de liquidez da opção

A sugestão só pode ser gerada se:
- open interest mínimo atingido
- bid mínimo atingido
- spread percentual dentro do limite
- vencimento dentro da política
- delta dentro da política

## 7. Objetivos do módulo

- aumentar renda sem deturpar a carteira
- melhorar preço de entrada em ações desejadas
- monitorar disciplina operacional
- transformar opções em overlay de renda, não em centro da estratégia

## 8. Entradas do módulo

O módulo depende de quatro blocos de dados:

### 8.1 Carteira
- posições
- quantidade
- preço médio
- marcação de posição núcleo
- permissão para covered call

### 8.2 Caixa
- caixa disponível
- caixa reservado para puts

### 8.3 Score da ação
- score final
- bucket
- quality_raw
- valuation_raw
- resumo da tese
- sinais de risco

### 8.4 Cadeia de opções
- tipo
- strike
- vencimento
- DTE
- bid/ask
- mid
- volume
- open interest
- delta
- theta
- IV
- preço do ativo

## 9. Saídas do módulo

### 9.1 Sugestões
Para cada sugestão:
- ticker
- tipo da sugestão
- vencimento
- DTE
- strike
- delta
- prêmio
- contratos
- capital requerido
- preço efetivo de entrada
- overlay_score
- motivo da sugestão
- risco principal
- regra de saída

### 9.2 Monitoramento
Para operações aceitas:
- lucro atual %
- DTE atual
- regra de saída atingida?
- sugestão de fechar?
- sugestão de rolar?

## 10. Critérios de elegibilidade — Covered Call

A ação só entra como candidata se:
- estiver na carteira
- quantidade >= 100 por contrato
- `allow_covered_call = true`
- não for posição núcleo intocável
- bucket não for `Rerating`
- desconto extremo não estiver aberto
- liquidez da opção for adequada

## 11. Critérios de elegibilidade — Cash-Secured Put

A ação só entra como candidata se:
- score final acima do mínimo
- bucket diferente de `Value Trap`
- o usuário aceitar comprar no strike
- existir caixa integral disponível
- liquidez da opção for adequada
- vencimento e delta estiverem dentro da política

## 12. Critérios de rejeição automática

### Covered Call
Rejeitar se:
- posição núcleo
- sem lote coberto
- bucket = `Rerating`
- bucket = `Qualidade com Desconto` e política proíbe
- spread ruim
- open interest baixo
- bid muito baixo
- delta fora da faixa

### Cash-Secured Put
Rejeitar se:
- bucket = `Value Trap`
- score final baixo
- caixa insuficiente
- spread ruim
- open interest baixo
- bid muito baixo
- delta fora da faixa

## 13. Score da sugestão

A sugestão de opção deve ter score próprio.

### Covered Call
- 30% qualidade da ação
- 20% maturidade da tese / valuation menos descontado
- 20% liquidez da opção
- 20% prêmio ajustado ao risco
- 10% aderência operacional

### Cash-Secured Put
- 30% qualidade da ação
- 25% atratividade do strike
- 20% liquidez da opção
- 15% prêmio ajustado ao risco
- 10% aderência operacional

## 14. Regras de saída

### Regra padrão
Fechar quando ocorrer o primeiro:
- 50% do lucro máximo
- 21 DTE

### Regras de exceção
- covered call pode ser recomprada antes se o ativo acelerar e a tese continuar forte
- put pode ser rolada se a tese seguir válida e o strike continuar aceitável
- se a tese piorar, o sistema não deve sugerir insistência mecânica

## 15. Regras de rolagem

### Rolagem de PUT
Sugerir rolagem quando:
- posição estiver pressionada
- DTE estiver curto
- a tese da ação continuar válida
- houver possibilidade de rolar com crédito aceitável

### Rolagem de CALL
Sugerir rolagem quando:
- usuário quiser manter a ação
- call estiver ameaçando exercício
- houver espaço para elevar strike ou estender prazo com racional aceitável

## 16. Escopo de UI

O frontend deve conter:

### Dashboard de opções
- covered calls sugeridas
- cash-secured puts sugeridas
- operações abertas
- alertas de saída

### Tela de carteira
- posições
- quantidade
- preço médio
- posição núcleo?
- covered call permitida?

### Tela de sugestão
- detalhe da sugestão
- motivo
- risco
- retorno
- regra de saída

### Tela de monitoramento
- opções abertas
- lucro %
- DTE
- fechar / rolar / manter

## 17. Separação de responsabilidades

### Motor principal
Seleciona ações.

### Overlay de opções
Seleciona operações de prêmio possíveis sobre as ações.

### Camada agentic
Explica:
- por que a sugestão existe
- qual o risco principal
- por que não sugerir determinada operação

## 18. Critérios de aceite do MVP

O módulo é aceito quando:
- lê carteira e caixa
- lê cadeia de opções
- aplica política configurável
- gera sugestões de covered call
- gera sugestões de cash-secured put
- monitora operações aceitas
- sugere saída por 21 DTE ou 50%
- não interfere no score oficial das ações
