from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.database_url import normalize_database_url

# pool_pre_ping: drop dead connections before use (helps after idle DB or restarts).
_engine_url = normalize_database_url(settings.DATABASE_URL)
engine = create_engine(_engine_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """One session per request; commit if the route finishes without error, else rollback."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Import models so SQLAlchemy registers tables on Base.metadata (Alembic + create_all).
from app.db import models as _models  # noqa: E402, F401
