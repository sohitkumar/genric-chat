# schemas.py — Defines the shape of data going IN and OUT of your API.
#
# WHY Pydantic models?
# 1. FastAPI uses these to automatically VALIDATE incoming requests.
# 2. They auto-generate the Swagger docs at /docs.
# 3. They act as a contract for API consumers.

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Body for sending a chat message. conversation_id groups turns into one thread."""

    message: str
    conversation_id: UUID = Field(default_factory=uuid4)
    # Set when the user is logged in; optional until you add auth on the client.
    user_id: UUID | None = None


class ChatResponse(BaseModel):
    """Immediate reply for non-streaming /chat."""

    reply: str


class LoadConversationRequest(BaseModel):
    """Body for loading stored messages for a thread (message text not required)."""

    conversation_id: UUID


class StoredMessageOut(BaseModel):
    """One persisted turn, returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    role: str
    content: str
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: UUID
    messages: list[StoredMessageOut]


class SignupRequest(BaseModel):
    email: str
    password: str

class SignupResponse(BaseModel):
    message: str
    user_id: UUID

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: UUID

class RecentConversationsResponse(BaseModel):
    conversations: list[ConversationHistoryResponse] = Field(default_factory=list)