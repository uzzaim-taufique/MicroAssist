"""Debugging agent (SCRUM-14): suggests likely causes and fixes for a
microcontroller problem.

It works like the recommendation agent: the user's text is sent to Google AI
with a versioned instruction prompt, and every failure becomes a
MicroAssistError with a friendly message from errors.py.
"""

import os
from pathlib import Path


from google import genai
from google.genai import errors as genai_errors
from google.genai import types

import errors

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "debugger_v1.md"
DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_MS = 30000  # stop waiting for Google AI after 30 seconds


def load_prompt(path=PROMPT_PATH):
    """Read the versioned debugging prompt from the repository."""
    return Path(path).read_text(encoding="utf-8")


def get_debug_help(problem, client=None, model=None):
    """Return Google AI's debugging advice for the described problem."""
    if not problem or not problem.strip():
        raise errors.MicroAssistError(errors.EMPTY_INPUT)

    if client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise errors.MicroAssistError(errors.MISSING_API_KEY)
        client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model or os.getenv("MICROASSIST_MODEL", DEFAULT_MODEL),
            contents=problem,
            config=types.GenerateContentConfig(
                system_instruction=load_prompt(),
                http_options=types.HttpOptions(timeout=TIMEOUT_MS),
            ),
        )
    except genai_errors.APIError as exc:
        raise errors.MicroAssistError(errors.SERVICE_ERROR) from exc
    except errors.TIMEOUT_EXCEPTIONS as exc:
        raise errors.MicroAssistError(errors.TIMED_OUT) from exc
    except errors.CONNECTION_EXCEPTIONS as exc:
        raise errors.MicroAssistError(errors.CONNECTION_FAILED) from exc

    text = response.text or ""
    if not text.strip():
        raise errors.MicroAssistError(errors.EMPTY_RESPONSE)
    return text