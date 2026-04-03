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

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm import get_chat_response, stream_chat_response

# prefix="/chat" means all routes in this file start with /chat
# tags help organize the Swagger docs at /docs
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Accept a user message and return the LLM's reply."""
    reply = get_chat_response(request.message)
    return ChatResponse(reply=reply)


@router.post("/stream")
def chat_stream(request: ChatRequest):
    """Stream LLM tokens to the client as Server-Sent Events.

    SSE protocol requires each event to be formatted as:
        data: <content>\n\n

    The "data: " prefix and double newline tell the client where each
    event starts and ends. Without this formatting, SSE clients (like
    Postman, browsers, or EventSource) see the events but can't read
    the data — which is why you'd get "(empty)" responses.
    """

    def sse_generator():
        for token in stream_chat_response(request.message):
            # A token might contain newlines (e.g. "end.\n\n### Heading").
            # In SSE, a bare \n inside a "data:" field would prematurely
            # end the event. So we split on \n and emit each piece as its
            # own "data:" event. Empty pieces (from consecutive \n\n) become
            # empty "data:" events, which the client reads back as \n.
            lines = token.split("\n")
            for line in lines:
                yield f"data: {line}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
