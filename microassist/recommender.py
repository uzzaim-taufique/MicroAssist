"""Sends project requirements to Google AI with the MicroAssist prompt (SCRUM-12)."""

import os
from pathlib import Path

from google import genai
from google.genai import types

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "recommender_v1.md"
DEFAULT_MODEL = "gemini-3.8-flash"


def load_prompt(path=PROMPT_PATH):
    """Read the versioned MicroAssist instruction prompt from the repository."""
    return Path(path).read_text(encoding="utf-8")


def get_recommendation(requirements, client=None, model=None):
    """Return Google AI's recommendation text for the given project requirements."""
    if not requirements:
        raise ValueError("Project requirements must not be empty.")

    if client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model or os.getenv("MICROASSIST_MODEL", DEFAULT_MODEL),
        contents=requirements,
        config=types.GenerateContentConfig(system_instruction=load_prompt()),
    )
    return response.text or "Google AI returned an empty response. Please try again."
