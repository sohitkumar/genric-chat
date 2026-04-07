# chat.py — The /chat API endpoints (regular + streaming).
#
# POST /chat persists user + assistant messages when the request completes.
# POST /chat/stream commits the user row first, then appends the assistant row
# after streaming finishes (separate DB session so the pool is not tied to the stream).
# POST /chat/load-conversation returns ordered history for a conversation_id.

from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import SessionLocal, get_db
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
    LoadConversationRequest,
    RecentConversationsResponse,
    StoredMessageOut,
)
from app.prompts import REJECTION_MESSAGE
from app.services.conversation_store import (
    ROLE_ASSISTANT,
    ROLE_USER,
    add_message,
    ensure_conversation,
    list_conversations_ordered,
    list_messages_ordered,
)
from app.services.intent_classifier import classify_query
from app.services.llm import get_chat_response, stream_chat_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Accept a user message, persist the turn, return the LLM reply."""

    ensure_conversation(db, request.conversation_id, request.user_id)
    add_message(
        db, request.conversation_id, ROLE_USER, request.message, user_id=request.user_id
    )

    if settings.GUARD_ENABLED and not classify_query(request.message):
        add_message(
            db,
            request.conversation_id,
            ROLE_ASSISTANT,
            REJECTION_MESSAGE,
            user_id=request.user_id,
        )
        return ChatResponse(reply=REJECTION_MESSAGE)

    reply = get_chat_response(request.message)
    add_message(
        db, request.conversation_id, ROLE_ASSISTANT, reply, user_id=request.user_id
    )
    return ChatResponse(reply=reply)


@router.post("/stream")
def chat_stream(request: ChatRequest):
    """Stream tokens; user message is committed before streaming, assistant row after."""

    if settings.GUARD_ENABLED and not classify_query(request.message):
        return StreamingResponse(rejection_stream(), media_type="text/event-stream")

    db = SessionLocal()
    try:
        ensure_conversation(db, request.conversation_id, request.user_id)
        add_message(
            db,
            request.conversation_id,
            ROLE_USER,
            request.message,
            user_id=request.user_id,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    conv_id = request.conversation_id
    user_id = request.user_id

    def sse_generator():
        pieces: list[str] = []
        try:
            for token in stream_chat_response(request.message):
                pieces.append(token)
                for line in token.split("\n"):
                    yield f"data: {line}\n\n"
        finally:
            full = "".join(pieces)
            if not full.strip():
                return
            inner = SessionLocal()
            try:
                add_message(inner, conv_id, ROLE_ASSISTANT, full, user_id=user_id)
                inner.commit()
            except Exception:
                inner.rollback()
                raise
            finally:
                inner.close()

    return StreamingResponse(sse_generator(), media_type="text/event-stream")


@router.post("/load-conversation", response_model=ConversationHistoryResponse)
def load_conversation(
    body: LoadConversationRequest,
    db: Session = Depends(get_db),
):
    """Return all stored messages for a conversation, oldest first."""
    rows = list_messages_ordered(db, body.conversation_id)
    return ConversationHistoryResponse(
        conversation_id=body.conversation_id,
        messages=[StoredMessageOut.model_validate(m) for m in rows],
    )

@router.post("/recent-conversations")
def recent_conversations(user_id: UUID, db: Session = Depends(get_db)):
    """Return the most recent conversations for a user."""
    rows = list_conversations_ordered(db, user_id)
    return RecentConversationsResponse(
        conversations=[ConversationHistoryResponse.model_validate(c) for c in rows],
    )


def rejection_stream():
    yield f"data: {REJECTION_MESSAGE}\n\n"
