# Handoff Report: Release Upside 12M (MVP)

Esta release marca a conclusão do primeiro módulo "Alpha" do B3 Screener, focado em potencial de valorização de 12 meses. O sistema agora possui dois motores independentes operando em paralelo.

## 📍 Estado Atual da Release

| Item | Status | Observação |
| :--- | :--- | :--- |
| **Screener Base** | 🟢 Estável | Motor de Qualidade/Dividendos operacional. |
| **Upside 12M** | 🟢 Concluído | Motor de Valorização/Re-rating operacional. |
| **API Backend** | 🟢 Operacional | Endpoints integrados e com suporte a jobs. |
| **Frontend UI** | 🟢 Operacional | Dashboard dedicado em `/upside` e detalhes. |

---

## 🛠️ Guia de Operação (Upside 12M)

### URLs Principais
- **Dashboard de Valorização**: [localhost:3000/upside](http://localhost:3000/upside)
- **Documentação de API**: [localhost:8000/docs#upside12m](http://localhost:8000/docs#upside12m)

### Jobs e Manutenção
Para processar os dados do novo módulo:
```powershell
# Execução via Docker
docker compose -f infra/docker-compose.yml exec backend python app/jobs/recalculate_upside12m.py
```

### Providers e Dados
- **Preços e Alvos**: Yahoo Finance (Provider Provisório).
- **Dados Contábeis**: CVM (Snapshot Anual/Trimestral).

---

## ⚠️ Limitações e Débitos Técnicos
1. **Histórico de Snapshots**: O componente de "Re-rating" atinge precisão total conforme a base histórica cresce. No lançamento, os scores tendem a ser mais influenciados pelo Upside de Research.
2. **Normalização Setorial**: Implementamos isenção de dívida para bancos, mas outros setores com CAPEX intensivo (ex: Elétricas/Saneamento) podem exigir calibração futura de thresholds de alavancagem.
3. **Estabilidade do Provider**: Instabilidade ocasional na API do Yahoo pode gerar falhas pontuais de coleta de preço atual.

---

## 🎯 Próxima Fase: Módulo de Opções

O projeto está configurado para iniciar a fase de **Opções (Income Strategist)**.

**Objetivos da Próxima Etapa:**
- Ingestão de séries de opções da B3 (InstrumentsConsolidated).
- Cálculo de *Moneyness*, *Time Decay* e Prêmios.
- Sugeridor de **Lançamento Coberto** (Covered Calls) para o Top 20 do Ranking.
- Sugeridor de **Venda de Puts** (Cash-Secured Puts) para alvos do Upside 12M.

**Documentos de Referência Criados:**
- `docs/OPTIONS_OVERLAY_PRD.md`
- `docs/OPTIONS_API_CONTRACT.md`
- `docs/OPTIONS_IMPLEMENTATION_CHECKLIST.md`

---
**Recursos Consolidados:**
- Documentação Técnica: [docs/UPSIDE_12M_MODULE.md](docs/UPSIDE_12M_MODULE.md)
- Guia de Execução Atualizado: [docs/EXECUTION_GUIDE.md](docs/EXECUTION_GUIDE.md)
