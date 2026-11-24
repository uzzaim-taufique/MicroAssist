"""Error messages shown to the user (SCRUM-8)."""
 
import importlib
 
# google-genai 2.x sends requests with the "httpx" library and 3.x with "httpx2".
# Both have the same exception classes, so we catch whichever ones exist.
_HTTP_LIBS = []
for _name in ("httpx", "httpx2"):
    try:
        _HTTP_LIBS.append(importlib.import_module(_name))
    except ImportError:
        pass
 
# Google AI did not answer in time.
TIMEOUT_EXCEPTIONS = tuple(lib.TimeoutException for lib in _HTTP_LIBS)
# No internet / could not reach Google AI (TimeoutException is a subclass,
# so always check TIMEOUT_EXCEPTIONS first).
CONNECTION_EXCEPTIONS = tuple(lib.TransportError for lib in _HTTP_LIBS) + (OSError,)
 
EMPTY_INPUT = "Please enter your project requirements."
MISSING_API_KEY = ("API key not found. Add GEMINI_API_KEY to your .env file "
                   "and try again.")
CONNECTION_FAILED = ("Could not connect to Google AI. Check your internet "
                     "connection and try again.")
TIMED_OUT = "Google AI took too long to respond. Please try again in a moment."
SERVICE_ERROR = ("Google AI returned an error. Check that your API key is "
                 "correct, or try again later.")
EMPTY_RESPONSE = ("No recommendation was received. Please try again or "
                  "describe your project in more detail.")
BUSY = ("Google AI is busy right now (too many requests). Please wait a "
        "minute and try again.")
DAILY_LIMIT = ("The free daily limit for Google AI has been reached. Try again "
               "tomorrow, or set MICROASSIST_MODEL in .env to another model.")
 
 
def api_error_message(exc):
    """Choose the right friendly message for an error returned by Google AI (SCRUM-33).
 
    429 = quota / daily limit reached, 500/502/503/504 = Google is overloaded
    or timed out on its side. Anything else (for example 400/401/403, which a
    wrong API key causes) keeps the "check your API key" message.
    """
    code = getattr(exc, "code", None)
    if code == 429:
        return DAILY_LIMIT
    if code in (500, 502, 503, 504):
        return BUSY
    return SERVICE_ERROR
 
 
class MicroAssistError(Exception):
    """An error with a friendly message that is safe to show to the user."""
