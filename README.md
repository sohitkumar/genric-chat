# Pharma chatbot API

FastAPI service for a pharma-themed chat assistant backed by OpenAI. Messages and users are stored in PostgreSQL. An optional intent classifier can reject off-topic questions before the main model runs.

## Prerequisites

- Python 3.10+ (recommended)
- A running PostgreSQL instance and an empty database for the app

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set OPENAI_API_KEY and DATABASE_URL (see below)
```

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `DATABASE_URL` | Yes | PostgreSQL URL, e.g. `postgresql+psycopg://USER:PASSWORD@localhost:5432/DBNAME` |
| `MODEL_NAME` | No | Main chat model (default `gpt-4o-mini`) |
| `CLASSIFIER_MODEL_NAME` | No | Model for intent classification (default `gpt-4o-mini`) |
| `GUARD_ENABLED` | No | If `true`, classify queries before the main LLM (default `true`) |

On startup the app runs **Alembic migrations to head** automatically, so the schema stays in sync with `app/db/models.py` revisions in `alembic/versions/`.

## Run

```bash
python main.py
```

Or with reload from the project root:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API base: http://127.0.0.1:8000  
- Interactive docs: http://127.0.0.1:8000/docs  

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Simple hello payload |
| `GET` | `/health` | App liveness; checks database connectivity |
| `POST` | `/user/signup` | Create user (bcrypt password hash) |
| `POST` | `/user/login` | Login; returns `user_id` |
| `POST` | `/chat/` | Chat; optional `conversation_id`, `user_id` |
| `POST` | `/chat/stream` | Same body as `/chat/`, SSE stream |
| `POST` | `/chat/load-conversation` | Load message history by `conversation_id` |
| `POST` | `/chat/recent-conversations` | Recent threads for a `user_id` (query param) |

### Example: chat

```bash
curl -s -X POST http://127.0.0.1:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is acetaminophen used for?"}'
```

### Example: streaming

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize common NSAID risks."}' \
  --no-buffer
```

Full request/response shapes and client integration order are in [API.md](API.md).

## Project layout

```
genric/
├── main.py                 # FastAPI app, CORS, lifespan (migrations + engine dispose)
├── alembic.ini             # Alembic config
├── alembic/                # Migrations (env.py, versions/)
├── requirements.txt
├── API.md                  # Endpoint reference for frontends
├── instruction.md          # Codebase map and request flows
├── app/
│   ├── config.py           # Settings from .env
│   ├── routes/
│   │   ├── chat.py         # /chat routes
│   │   └── user.py         # /user routes
│   ├── models/
│   │   └── schemas.py      # Pydantic API models
│   ├── services/
│   │   ├── llm.py          # OpenAI sync + stream
│   │   ├── intent_classifier.py
│   │   └── conversation_store.py
│   ├── prompts/            # System / rejection copy
│   └── db/                 # SQLAlchemy models, session, URL helpers
└── .env                    # Local secrets (not committed; from .env.example)
```

For where to change behavior (prompts, guard, persistence), see [instruction.md](instruction.md).
