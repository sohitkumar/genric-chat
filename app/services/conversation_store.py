"""Persistence helpers for conversations and messages (used by chat routes)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message
from app.routes import user

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


def ensure_conversation(
    db: Session,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID | None,
) -> Conversation:
    """Return existing thread or create a row keyed by conversation_id."""
    conv = db.get(Conversation, conversation_id)
    if conv is not None:
        if user_id is not None and conv.user_id is None:
            conv.user_id = user_id
        return conv
    conv = Conversation(conversation_id=conversation_id, user_id=user_id)
    db.add(conv)
    db.flush()
    return conv


def add_message(
    db: Session,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    user_id: uuid.UUID | None = None,
) -> Message:
    """Persist a turn. user_id is optional; must reference an existing users.id if set."""
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        user_id=user_id,
    )
    db.add(msg)
    return msg


def list_messages_ordered(db: Session, conversation_id: uuid.UUID) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(db.scalars(stmt).all())

def list_conversations_ordered(db: Session, user_id: uuid.UUID) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(db.scalars(stmt).all())