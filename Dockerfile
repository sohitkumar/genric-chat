# FastAPI + Alembic; at runtime set OPENAI_API_KEY, DATABASE_URL, and optionally API_PUBLIC_URL / CORS_ORIGINS.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --shell /bin/bash app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
