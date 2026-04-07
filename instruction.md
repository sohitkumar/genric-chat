# How to understand this codebase

This document is a map of the project: what each part does, how a request flows through it, and where to edit when you change behavior.

---

## What the app does

- Exposes a **FastAPI** HTTP API for a **pharma-themed chatbot** powered by OpenAI.
- Optionally **classifies** the user query first; off-topic queries get a fixed rejection without calling the main model.
- **Persists** chat turns in **PostgreSQL** (users, conversations, messages).

---

## Mental model: three layers

When you read or change code, fit it into one of these:

| Layer | Role | Typical locations |
|--------|------|-------------------|
| **HTTP** | URLs, status codes, request/response shapes | `main.py`, `app/routes/`, `app/models/schemas.py` |
| **Use cases** | Business logic: guard, LLM calls, saving chat | `app/services/` |
| **Infrastructure** | Database, migrations, settings | `app/db/`, `alembic/`, `app/config.py` |

If something does not clearly belong to one layer, consider whether it should move or stay as a thin helper.

---

## Directory and file map

```
genric/
  main.py                 # FastAPI app, CORS, lifespan (migrations + engine dispose), includes routers
  instruction.md          # This guide
  .env                    # Local secrets (not committed); copy from .env.example
  requirements.txt      # Python dependencies

  app/
    config.py             # Settings from .env (OPENAI_API_KEY, DATABASE_URL, models, GUARD_ENABLED)
    routes/
      chat.py             # POST /chat, /chat/stream, /chat/load-conversation
    models/
      schemas.py          # Pydantic models: API request/response JSON shapes (not SQL tables)
    services/
      llm.py              # OpenAI chat completion (sync + stream helpers)
      intent_classifier.py# Pharma vs non-pharma gate
      conversation_store.py # DB helpers: ensure conversation, add/list messages
    prompts/
      __init__.py         # Prompt strings (e.g. rejection message)
    db/
      base.py             # SQLAlchemy DeclarativeBase
      models.py           # ORM table definitions (User, Conversation, Message)
      session.py          # Engine, SessionLocal, get_db dependency, URL normalization import
      database_url.py     # Ensures postgresql:// uses the psycopg3 driver (+psycopg)

  alembic/
    env.py                # Migration runtime: loads .env, sets DB URL, target_metadata
    versions/             # Revision scripts (e.g. initial schema)
  alembic.ini             # Alembic config (script location, etc.)
```

---

## Request flow: `POST /chat` (non-streaming)

1. **FastAPI** parses the body using **`ChatRequest`** in `app/models/schemas.py`.
2. **`chat.py`** calls **`ensure_conversation`** and **`add_message`** (user row) via **`conversation_store.py`** using a **`Session`** from **`get_db`** (`app/db/session.py`).
3. If **`GUARD_ENABLED`** and **`classify_query`** (`intent_classifier.py`) says off-topic, an assistant row with the rejection text is stored and returned.
4. Otherwise **`get_chat_response`** (`llm.py`) calls OpenAI; the reply is stored as an assistant **`Message`** and returned as **`ChatResponse`**.
5. **`get_db`** commits the transaction on success (or rolls back on error).

---

## Request flow: `POST /chat/stream`

- Same guard as above for rejected queries (no DB write in that branch).
- For allowed queries: user message is written in a **short-lived session** and committed **before** streaming starts (so the DB session is not held open for the whole stream).
- After the stream finishes, a **new** session appends the full assistant text.

---

## Request flow: `POST /chat/load-conversation`

- Body: **`LoadConversationRequest`** (conversation id only).
- Returns **`ConversationHistoryResponse`**: ordered list of stored messages (role, content, timestamps).

---

## Database and migrations

- **ORM tables** are defined in **`app/db/models.py`**. They describe PostgreSQL structure in Python.
- **Alembic** applies **versioned** SQL changes in **`alembic/versions/`**. Do not rely on manually editing production DB without a new revision.
- On **application startup**, **`main.py`** runs **`alembic upgrade head`** so the database is brought up to date automatically (no-op if already current).
- When you **change** `models.py`, you still create a new revision yourself, for example:

  ```bash
  alembic revision --autogenerate -m "describe change"
  ```

  Review the generated file, then commit it. The next app start applies it.

- **`DATABASE_URL`** belongs in **`.env`**. It may be `postgresql://...` or `postgresql+psycopg://...`; **`database_url.py`** normalizes bare `postgresql://` to use **psycopg v3**.

---

## Configuration (`.env`)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required; OpenAI API access |
| `DATABASE_URL` | Required; PostgreSQL connection string (user, password, host, port, database name) |
| `MODEL_NAME` | Main chat model (default `gpt-4o-mini`) |
| `CLASSIFIER_MODEL_NAME` | Model used for intent classification |
| `GUARD_ENABLED` | If true, run classifier before main LLM |

See **`.env.example`** for a template.

---

## How to run locally

1. Create a virtual environment, install dependencies: `pip install -r requirements.txt`
2. Copy **`.env.example`** to **`.env`** and fill in values (especially **`OPENAI_API_KEY`** and **`DATABASE_URL`**).
3. Ensure PostgreSQL is running and the target database exists.
4. From the project root: `python main.py` (or `uvicorn main:app --reload`).

Interactive API docs: **http://127.0.0.1:8000/docs**

---

## Where to change what

| Goal | Start here |
|------|------------|
| New endpoint or change URL | `app/routes/chat.py` (or add a new router and include it in `main.py`) |
| Change JSON the API accepts or returns | `app/models/schemas.py` |
| Change prompts or rejection text | `app/prompts/__init__.py` |
| Change LLM behavior or model calls | `app/services/llm.py` |
| Tighten or relax the pharma guard | `app/services/intent_classifier.py` |
| Change how messages are saved or loaded | `app/services/conversation_store.py` |
| Add or rename tables/columns | `app/db/models.py` + new Alembic revision |
| Change DB connection or session behavior | `app/db/session.py`, `app/db/database_url.py` |
| Change env var names or defaults | `app/config.py` |
| Migration environment (URL loading, metadata) | `alembic/env.py` |

---

## Pydantic `schemas` vs SQLAlchemy `models`

- **`app/models/schemas.py`**: what clients send and receive over HTTP (validated JSON).
- **`app/db/models.py`**: how rows are stored in PostgreSQL.

They often look similar but serve different purposes; keeping both avoids leaking internal columns or DB details into the public API.

---

## Suggested reading order for newcomers

1. `main.py` — how the app boots and wires routers  
2. `app/routes/chat.py` — actual HTTP behavior  
3. `app/models/schemas.py` — API contract  
4. `app/services/llm.py` and `intent_classifier.py` — intelligence layer  
5. `app/services/conversation_store.py` + `app/db/models.py` — persistence  

After that, skim `alembic/env.py` and one file under `alembic/versions/` to see how schema changes are recorded.
