# prompts/__init__.py — Loads prompt text files from this folder.
#
# WHY load prompts from files instead of hardcoding in Python?
# - Prompts change frequently. Editing a .txt file is faster than
#   finding the right line in Python and worrying about quote escaping.
# - Domain experts (e.g., pharmacists) can review .txt files without
#   knowing Python.
# - git diff shows prompt changes in plain English, not buried in code.
#
# HOW does it work?
# pathlib.Path(__file__) gives us the path to THIS file (__init__.py).
# .parent gives us the folder this file is in (app/prompts/).
# We then join the filename and read the text.
#
# Prompts are loaded ONCE at module level (when the app starts), not on
# every request. This avoids reading the disk on each API call.

from pathlib import Path

# The folder where all .txt prompt files live
_PROMPTS_DIR = Path(__file__).parent


def load_prompt(filename: str) -> str:
    """Read a prompt file from the prompts/ folder and return its text.

    Usage:
        from app.prompts import load_prompt
        system_prompt = load_prompt("system.txt")
    """
    path = _PROMPTS_DIR / filename
    return path.read_text().strip()


# Pre-load all prompts at startup so they're ready to use everywhere.
# Import these directly:
#   from app.prompts import SYSTEM_PROMPT, CLASSIFIER_PROMPT, REJECTION_MESSAGE

SYSTEM_PROMPT = load_prompt("system.txt")
CLASSIFIER_PROMPT = load_prompt("classifier.txt")
REJECTION_MESSAGE = load_prompt("rejection.txt")
