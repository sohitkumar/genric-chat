# LLM Chatbot API

A minimal FastAPI chatbot that connects to an OpenAI-compatible LLM. Supports both regular and streaming responses.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Edit .env and add your actual API key
```

## Run

```bash
python main.py
```

Server starts at http://127.0.0.1:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Hello world |
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send a message, get the full reply at once |
| `POST` | `/chat/stream` | Send a message, get tokens streamed in real-time (SSE) |

### Example: Chat

```bash
curl -X POST http://127.0.0.1:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}'
```

### Example: Streaming

```bash
curl -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}' \
  --no-buffer
```

## Project Structure

```
genric/
├── main.py                 # App entrypoint
├── .env                    # API keys (not committed)
├── .env.example            # Template for .env
├── requirements.txt        # Dependencies
├── app/
│   ├── config.py           # Loads settings from .env
│   ├── models/
│   │   └── schemas.py      # Request/response models
│   ├── routes/
│   │   └── chat.py         # Chat endpoints
│   └── services/
│       └── llm.py          # LLM interaction logic
└── venv/                   # Virtual environment (not committed)
```

## Interactive Docs

Once the server is running, open http://127.0.0.1:8000/docs for the auto-generated Swagger UI.
