from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(title=settings.app_name)

local_dev_origin_regex = (
    r"^http://(localhost|127\.0\.0\.1):\d+$"
    if settings.environment == "dev"
    else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=local_dev_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base health check outside /api/v1
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

# All other business routes under /api/v1
app.include_router(api_router, prefix="/api/v1")
