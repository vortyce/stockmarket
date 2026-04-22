# Guia de Execução e Validação: B3 Screener

Este documento consolida os comandos e procedimentos necessários para subir o stack completo e validar o motor de análise via navegador.

## 1. Comandos Docker

Navegue até a pasta `infra/` ou use os caminhos abaixo:

### Build e Inicialização
```powershell
# Build das imagens (Backend e Frontend)
docker compose -f infra/docker-compose.yml build

# Subir todo o stack em background
docker compose -f infra/docker-compose.yml up -d
```

### Monitoramento e Logs
```powershell
# Ver logs em tempo real
docker compose -f infra/docker-compose.yml logs -f

# Ver apenas logs do backend
docker compose -f infra/docker-compose.yml logs -f backend
```

### Finalização
```powershell
# Parar e remover containers
docker compose -f infra/docker-compose.yml down
```

---

## 2. URLs de Acesso

| Serviço | URL | Observação |
| :--- | :--- | :--- |
| **Frontend** | [http://localhost:3000](http://localhost:3000) | Dashboard e Screener |
| **Backend API** | [http://localhost:8000](http://localhost:8000) | JSON Root |
| **Upside 12M (Alpha)** | [http://localhost:3000/upside](http://localhost:3000/upside) | Novo Dashboard de Valorização |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Documentação interativa |
| **Healthcheck** | [http://localhost:8000/health](http://localhost:8000/health) | Status do DB e Redis |

---

## 3. Checklist de Validação Manual

Após subir o stack, realize estas verificações no navegador:

- [ ] **Home/Dashboard**: Acesse `localhost:3000`. Verifique se os cartões de stats (Total Coberto, Melhor Score) aparecem e se o Top 5 ranking está populado.
- [ ] **Ranking Top 20**: Navegue para a aba "Top 20". Os tickers (PETR4, BBAS3, etc.) devem aparecer com badges coloridos de Rating e indicação de Buckets.
- [ ] **Screener**: Teste a busca na aba "Screener". Pesquise por "PETR" para filtrar a tabela em tempo real.
- [ ] **Detalhe da Empresa**: Clique em "Ver Análise" de qualquer ticker. Verifique se as barras de progresso dos 5 blocos (Qualidade, Valuation, etc.) refletem o score calculado.
- [ ] **Módulo Upside 12M**: Acesse `localhost:3000/upside`. Verifique se o Top 20 de potencial de valorização aparece (ABEV3, BBAS3, etc.) e se o detalhamento por ticker mostra a decomposição correta dos componentes (Re-rating, Recuperação Operacional, Assimetria).
- [ ] **API**: Abra [localhost:8000/api/v1/companies](http://localhost:8000/api/v1/companies) e confirme se o JSON dos ativos é retornado.

---

## 4. Execução dos Jobs (Data Pipeline)

Para atualizar a base de dados em execução, você pode rodar os comandos diretamente no container do backend:

```powershell
# Ingestão B3 (Cadastro de Empresas)
docker compose -f infra/docker-compose.yml exec backend python app/jobs/ingest_b3.py

# Ingestão CVM (Financeiros 2022-2023)
docker compose -f infra/docker-compose.yml exec backend python app/jobs/ingest_cvm.py --years 2022 2023

# Ingestão Mercado (Cotações Reais Yahoo)
docker compose -f infra/docker-compose.yml exec backend python app/jobs/ingest_market.py

# Recalcular Scores e Rankings (Screener Base)
docker compose -f infra/docker-compose.yml exec backend python app/jobs/recalculate_scores.py

# Recalcular Upside 12M (Módulo Alpha)
docker compose -f infra/docker-compose.yml exec backend python app/jobs/recalculate_upside12m.py
```

---

## 5. Pendências e Próximos Passos

### ⚠️ Provisório e Melhorias Necessárias
- **Yahoo Provider**: O coletor Yahoo (`yfinance`) é provisório. Para produção, recomenda-se integração com APIs profissionais (Bloomberg, Refinitiv ou CVM direto) para garantir estabilidade e campos como *Free Cash Flow* real.
- **Número de Ações**: Atualmente, ratios per-share (como EPS) estão simplificados. Falta extrair o número total de ações do formulário cadastral da CVM para cálculos mais precisos de Value.
- **Liquidez Intraday**: A liquidez está usando indicadores estáticos ou de free float. Falta integrar o volume médio diário (ADTV) real.

### 🛠️ Módulo de Opções (Próxima Fase)
- Implementação dos Sugeridores de **Lançamento Coberto** e **Puts**.
- Monitor de Gregas e volatilidade implícita.

### 🚀 Preparação para Produção
- Configurar Nginx como proxy reverso.
- Implementar autenticação (JWT) e proteção de endpoints de Ingestão.
- Migrar DB para RDS/Gerenciado.
