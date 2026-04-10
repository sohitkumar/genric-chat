# config.py — Loads settings from your .env file into a typed Python object.
#
# WHY do we need this?
# Instead of calling os.getenv("OPENAI_API_KEY") scattered across many files,
# we load everything ONCE here. If a required key is missing, the app crashes
# at startup with a clear error — not later when a user hits the chat endpoint.
#
# HOW does it work?
# pydantic-settings reads your .env file and maps each variable to a field below.
# It also validates types (e.g., ensures OPENAI_API_KEY is a non-empty string).

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Your OpenAI API key — required, app won't start without it
    OPENAI_API_KEY: str

    # Which model to use — defaults to gpt-4o-mini (cheap and fast, good for learning)
    MODEL_NAME: str = "gpt-4o-mini"

    CLASSIFIER_MODEL_NAME: str = "gpt-4o-mini"

    GUARD_ENABLED: bool = True

    DATABASE_URL: str

    # Public base URL of this API (e.g. https://api.example.com or http://EC2_IP:8000). Used for OpenAPI/Swagger
    # "Try it" and server list. Set when behind a reverse proxy or when docs should show the real URL.
    API_PUBLIC_URL: str | None = None

    # Comma-separated browser origins allowed to call the API, or "*" for any origin (dev only).
    CORS_ORIGINS: str = "*"
    # Tell pydantic-settings to read from a .env file in the project root
    model_config = SettingsConfigDict(env_file=".env")


# Create one global instance — import this wherever you need settings
# e.g., from app.config import settings
settings = Settings()
