"""Sends project requirements to Google AI with the MicroAssist prompt (SCRUM-12).

Error handling (SCRUM-20): every failure is turned into a MicroAssistError
with a friendly message from errors.py, so the user never sees a traceback
and the API key is never shown.
"""

import os
from pathlib import Path

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

import errors

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "recommender_v1.md"
DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_MS = 30000  # stop waiting for Google AI after 30 seconds


def load_prompt(path=PROMPT_PATH):
    """Read the versioned MicroAssist instruction prompt from the repository."""
    return Path(path).read_text(encoding="utf-8")


def get_recommendation(requirements, client=None, model=None):
    """Return Google AI's recommendation text for the given project requirements."""
    # Empty input or only spaces: stop here, before any API call.
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
                http_options=types.HttpOptions(timeout=TIMEOUT_MS),
            ),
        )
    except genai_errors.APIError as exc:          # wrong key, quota, server error
        raise errors.MicroAssistError(errors.SERVICE_ERROR) from exc
    except httpx.TimeoutException as exc:         # Google AI too slow
        raise errors.MicroAssistError(errors.TIMED_OUT) from exc
    except (httpx.TransportError, OSError) as exc:  # no internet
        raise errors.MicroAssistError(errors.CONNECTION_FAILED) from exc

    text = response.text or ""
    if not text.strip():
        raise errors.MicroAssistError(errors.EMPTY_RESPONSE)
    return text