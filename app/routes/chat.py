# chat.py — The /chat API endpoints (regular + streaming).
#
# WHY use APIRouter instead of putting this in main.py?
# As your app grows, you'll add more endpoints (e.g., /history, /feedback).
# Each group of related endpoints gets its own router file.
# main.py just "includes" them — keeping it clean.
#
# TWO endpoints live here:
#   POST /chat        — Returns the full reply at once (original)
#   POST /chat/stream — Streams tokens in real-time via Server-Sent Events (SSE)
#
# Both endpoints run the intent classifier FIRST. If the query is not
# pharmaceutical-related, we return a rejection without calling the main LLM.

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.prompts import REJECTION_MESSAGE
from app.services.intent_classifier import classify_query
from app.services.llm import get_chat_response, stream_chat_response

# prefix="/chat" means all routes in this file start with /chat
# tags help organize the Swagger docs at /docs
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Accept a user message and return the LLM's reply."""

    # Guard: check if the query is pharma-related before calling the main LLM
    if settings.GUARD_ENABLED and not classify_query(request.message):
        return ChatResponse(reply=REJECTION_MESSAGE)

    reply = get_chat_response(request.message)
    return ChatResponse(reply=reply)


@router.post("/stream")
def chat_stream(request: ChatRequest):
    """Stream LLM tokens to the client as Server-Sent Events.

    If the query is off-topic, we return the rejection as a single
    SSE event instead of streaming — no point streaming a static message.
    """

    # Guard: reject non-pharma queries before streaming
    if settings.GUARD_ENABLED and not classify_query(request.message):
        return StreamingResponse(rejection_stream(), media_type='text/event-stream')

    def sse_generator():
        for token in stream_chat_response(request.message):
            lines = token.split("\n")
            for line in lines:
                yield f"data: {line}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

def rejection_stream():
    yield f"data: {REJECTION_MESSAGE}\n\n"
