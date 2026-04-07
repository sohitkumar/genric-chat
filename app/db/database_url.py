"""Normalize DATABASE_URL so SQLAlchemy uses psycopg v3, not psycopg2.

A bare ``postgresql://`` URL selects the legacy psycopg2 dialect, which fails if only
``psycopg`` (v3) is installed. We rewrite to ``postgresql+psycopg://``.
"""


def normalize_database_url(url: str) -> str:
    u = url.strip()
    # Already specifies a driver (psycopg, asyncpg, psycopg2, etc.)
    if "+" in u.split("://", 1)[0]:
        return u
    if u.startswith("postgresql://"):
        return "postgresql+psycopg://" + u[len("postgresql://") :]
    if u.startswith("postgres://"):
        return "postgresql+psycopg://" + u[len("postgres://") :]
    return u
