# llm.py — Handles all communication with the LLM (OpenAI).
#
# WHY a separate service file?
# Your route (chat.py) should only handle HTTP concerns (request in, response out).
# The actual "talk to the LLM" logic lives here. This separation means:
# - You can swap OpenAI for another provider by changing ONLY this file.
# - You can test this function independently without running the whole server.
# - Your route stays clean and readable.
#
# HOW does it work?
# We create ONE OpenAI client at module level (so it's reused across requests),
# then provide functions to get a complete response OR stream it token-by-token.

from collections.abc import Generator

from openai import OpenAI
from app.config import settings

# Create the client once — it manages connection pooling internally.
# The api_key is read from our Settings object (which loaded it from .env).
client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url="https://chat.int.bayer.com/api/v2",)


def _build_messages(user_message: str) -> list[dict]:
    """Build the messages list for the LLM. Shared by both streaming and non-streaming."""
    return [
        # "system" message sets the LLM's behavior/personality.
        # Change this to customize how your chatbot responds.
        {"role": "system", "content": "You are a helpful assistant."},
        # "user" message is what the user typed.
        {"role": "user", "content": user_message},
    ]


def get_chat_response(user_message: str) -> str:
    """Send a message to the LLM and return its reply as a string."""

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=_build_messages(user_message),
    )

    # response.choices is a list — the first choice is the main reply.
    # .message.content is the actual text string.
    return response.choices[0].message.content


def stream_chat_response(user_message: str) -> Generator[str, None, None]:
    """Stream LLM tokens one-by-one as they are generated.

    With stream=True, the OpenAI SDK returns an iterator of small
    ChatCompletionChunk objects instead of one big response.
    Each chunk's .choices[0].delta.content holds the next few tokens
    (or None when the stream is finished).

    This function is a Python *generator* — it yields each piece of text
    as it arrives, so the caller can forward it to the client in real-time.
    """

    stream = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=_build_messages(user_message),
        stream=True,
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        # delta.content is None for the final chunk (the stream-end signal)
        if content is not None:
            yield content
