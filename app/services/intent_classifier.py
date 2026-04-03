# intent_classifier.py — Classifies user intent before reaching the main LLM.
#
# WHY a separate classifier instead of relying on the system prompt alone?
# The system prompt tells the LLM "only answer pharma questions", but
# LLMs can be tricked (prompt injection). The classifier is a separate,
# cheap LLM call that runs BEFORE the main one. It has one job: YES or NO.
# If it says NO, we never call the main LLM — saving cost and blocking
# off-topic queries at the door.
#
# HOW does it work?
# 1. Send the user's message to a fast/cheap model with the classifier prompt
# 2. The model returns "YES" or "NO"
# 3. We return True (pharma) or False (not pharma)
#
# The classifier uses CLASSIFIER_MODEL_NAME from config, which can be a
# cheaper model than the main one — classification is a simple task.

from app.config import settings
from app.prompts import CLASSIFIER_PROMPT
from app.services.llm import client


def classify_query(user_message: str) -> bool:
    """Return True if the query is pharmaceutical-related, False otherwise.

    Makes a short LLM call with the classifier prompt. The LLM is asked
    to respond with exactly "YES" or "NO". We parse that single word
    to make the decision.
    """
    response = client.chat.completions.create(
        model=settings.CLASSIFIER_MODEL_NAME,
        messages=[
            {"role": "system", "content": CLASSIFIER_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    answer = response.choices[0].message.content.strip().upper()
    return answer == "YES"
