# schemas.py — Defines the shape of data going IN and OUT of your API.
#
# WHY Pydantic models?
# 1. FastAPI uses these to automatically VALIDATE incoming requests.
#    If a user sends bad data (e.g., missing "message"), FastAPI returns
#    a clear 422 error without you writing any validation code.
# 2. They auto-generate the Swagger docs at /docs — so your API is
#    self-documenting.
# 3. They act as a contract: anyone reading this file instantly knows
#    what your API expects and returns.

from pydantic import BaseModel


class ChatRequest(BaseModel):
    # The user's message to send to the LLM
    message: str


class ChatResponse(BaseModel):
    # The LLM's reply
    reply: str
