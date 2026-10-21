"""Error messages shown to the user (SCRUM-8)."""
 
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
 
 
class MicroAssistError(Exception):
    """An error with a friendly message that is safe to show to the user."""
