# Quickstart

## 1. Suba a infraestrutura
```bash
docker compose -f infra/docker-compose.yml up --build
```

## 2. Backend
- validar `/health`
- configurar `.env`
- rodar migrations com Alembic

## 3. Frontend
- validar página inicial
- apontar `NEXT_PUBLIC_API_URL` para o backend

## 4. Ordem de implementação
1. migrations e banco
2. CRUD e API mínima
3. ingestão CVM/B3
4. enriquecimento de mercado
5. scoring
6. ranking
7. dashboards
8. camada agentic auxiliar

## 5. Documentos principais
- `docs/B3_Screener_PRD_Tecnico.md`
- `docs/IMPLEMENTATION_CHECKLIST.md`
- `docs/API_CONTRACT.md`
