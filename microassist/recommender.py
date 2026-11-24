
"""Sends project requirements to Google AI with the MicroAssist prompt (SCRUM-12).

Function calling (SCRUM-16): Gemini is given the database search tool, so it
looks up real specifications in data/microcontrollers.json before it
recommends a part. The google-genai SDK runs the tool automatically.

Error handling (SCRUM-20): every failure is turned into a MicroAssistError
with a friendly message from errors.py, so the user never sees a traceback
and the API key is never shown.
"""

import logging
import os
from pathlib import Path

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

import errors
from microassist.database import search_microcontrollers

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "recommender_v2.md"
DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_MS = 30000
MAX_TOOL_CALLS = 5


class _HideAfcAdvice(logging.Filter):
    """Hide the SDK's direct automatic function calling advice."""

    def filter(self, record):
        return not record.getMessage().startswith(
            "Direct use of automatic function calling"
        )


logging.getLogger("google_genai.models").addFilter(_HideAfcAdvice())


def load_prompt(path=PROMPT_PATH):
    """Read the versioned MicroAssist instruction prompt."""
    return Path(path).read_text(encoding="utf-8")


def get_recommendation(requirements, client=None, model=None):
    """Return Google's recommendation for the given requirements."""

    if not requirements or not requirements.strip():
        raise errors.MicroAssistError(errors.EMPTY_INPUT)

    if client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise errors.MicroAssistError(errors.MISSING_API_KEY)
        client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model or os.getenv("MICROASSIST_MODEL", DEFAULT_MODEL),
            contents=requirements,
            config=types.GenerateContentConfig(
                system_instruction=load_prompt(),
                tools=[search_microcontrollers],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    maximum_remote_calls=MAX_TOOL_CALLS
                ),
                http_options=types.HttpOptions(timeout=TIMEOUT_MS),
            ),
        )

    except genai_errors.APIError as exc:
        raise errors.MicroAssistError(
            errors.api_error_message(exc)
        ) from exc

    except errors.TIMEOUT_EXCEPTIONS as exc:
        raise errors.MicroAssistError(
            errors.TIMED_OUT
        ) from exc

    except errors.CONNECTION_EXCEPTIONS as exc:
        raise errors.MicroAssistError(
            errors.CONNECTION_FAILED
        ) from exc

    text = response.text or ""

    if not text.strip():
        raise errors.MicroAssistError(errors.EMPTY_RESPONSE)

    return text
