from fastapi import APIRouter
from app.api.routes import companies, rankings, scores, jobs, upside12m, portfolio, options

api_router = APIRouter()
api_router.include_router(companies.router)
api_router.include_router(rankings.router)
api_router.include_router(scores.router)
api_router.include_router(jobs.router)
api_router.include_router(upside12m.router)
api_router.include_router(portfolio.router)
api_router.include_router(options.router)
