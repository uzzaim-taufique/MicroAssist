
"""Router agent (SCRUM-15): decides which agent should answer a request.

Google AI classifies the request as "selection", "debugging" or "unclear".
Any reply that is not one of these words is treated as "unclear", so the
app never sends a request to the wrong agent because of an odd AI reply.
"""

import os
from pathlib import Path

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

import errors

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "router_v1.md"
DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_MS = 15000  # routing is a short answer, so wait at most 15 seconds

SELECTION = "selection"
DEBUGGING = "debugging"
UNCLEAR = "unclear"
LABELS = (SELECTION, DEBUGGING, UNCLEAR)

CLARIFICATION = ("I'm not sure what you need yet. Are you choosing a "
                 "microcontroller for a new project, or fixing a problem with "
                 "an existing one? Please describe it in a bit more detail.")


def load_prompt(path=PROMPT_PATH):
    """Read the versioned router prompt from the repository."""
    return Path(path).read_text(encoding="utf-8")


def parse_label(reply):
    """Turn the AI's reply into one of LABELS; anything else is UNCLEAR."""
    words = (reply or "").strip().lower().split()
    if not words:
        return UNCLEAR
    word = words[0].strip(".,!:;\"'`*")
    return word if word in LABELS else UNCLEAR


def route(request, client=None, model=None):
    """Return "selection", "debugging" or "unclear" for the user's request."""
    if not request or not request.strip():
        raise errors.MicroAssistError(errors.EMPTY_INPUT)

    if client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise errors.MicroAssistError(errors.MISSING_API_KEY)
        client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model or os.getenv("MICROASSIST_MODEL", DEFAULT_MODEL),
            contents=request,
            config=types.GenerateContentConfig(
                system_instruction=load_prompt(),
                temperature=0,
                http_options=types.HttpOptions(timeout=TIMEOUT_MS),
            ),
        )
    except genai_errors.APIError as exc:
        raise errors.MicroAssistError(errors.SERVICE_ERROR) from exc
    except httpx.TimeoutException as exc:
        raise errors.MicroAssistError(errors.TIMED_OUT) from exc
    except (httpx.TransportError, OSError) as exc:
        raise errors.MicroAssistError(errors.CONNECTION_FAILED) from exc

    return parse_label(response.text)
