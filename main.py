# main.py — The entrypoint of your application.
#
# Lifespan: run Alembic migrations to head on startup, then dispose the engine on shutdown.

from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.db.session import engine
from app.routes.chat import router as chat_router
from app.routes.user import router as user_router


def _cors_allow_origins() -> list[str]:
    raw = settings.CORS_ORIGINS.strip()
    if raw == "*":
        return ["*"]
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins if origins else ["*"]


def _run_alembic_upgrade_to_head() -> None:
    """Apply all pending migrations. Safe to call every boot: no-op when already at head."""
    ini_path = Path(__file__).resolve().parent / "alembic.ini"
    if not ini_path.is_file():
        raise RuntimeError(f"Alembic config not found: {ini_path}")
    cfg = Config(str(ini_path))
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_alembic_upgrade_to_head()
    yield
    engine.dispose()


_fastapi_kw: dict = dict(
    title="LLM Chatbot API",
    description="A minimal chatbot API powered by OpenAI",
    lifespan=lifespan,
)
if settings.API_PUBLIC_URL:
    _fastapi_kw["servers"] = [{"url": settings.API_PUBLIC_URL.rstrip("/")}]
app = FastAPI(**_fastapi_kw)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(user_router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    """Liveness: always cheap. DB check uses the same engine as the app (see .env DATABASE_URL)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "detail": str(exc),
            },
        )
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
