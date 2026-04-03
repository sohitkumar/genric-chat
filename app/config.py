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

    # Tell pydantic-settings to read from a .env file in the project root
    model_config = SettingsConfigDict(env_file=".env")


# Create one global instance — import this wherever you need settings
# e.g., from app.config import settings
settings = Settings()
