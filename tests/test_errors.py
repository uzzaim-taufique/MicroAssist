"""SCRUM-21: acceptance checks for empty input and AI failures; no API calls."""
import unittest
from types import SimpleNamespace
from unittest import mock
import httpx
from google.genai import errors as genai_errors
import errors
import main
from microassist import recommender

FAKE_KEY = "test-key-12345"

def fake_client(reply=None, error=None):
    client = mock.MagicMock()
    if error is not None:
        client.models.generate_content.side_effect = error
    else:
        client.models.generate_content.return_value = SimpleNamespace(text=reply)
    return client

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict("os.environ", {"GEMINI_API_KEY": FAKE_KEY}, clear=True)
        self.dotenv = mock.patch("main.load_dotenv")
        self.env.start()
        self.addCleanup(self.env.stop)
        self.dotenv.start()
        self.addCleanup(self.dotenv.stop)
        # Block real SDK clients even if production code changes its control flow.
        self.client_class = mock.patch("microassist.recommender.genai.Client", return_value=fake_client(reply="ESP32"))
        self.client_class.start()
        self.addCleanup(self.client_class.stop)

    def check_message(self, error, expected):
        with mock.patch("microassist.recommender.genai.Client", return_value=fake_client(error=error)):
            with self.assertRaises(errors.MicroAssistError) as ctx:
                recommender.get_recommendation("room monitor")
        self.assertEqual(str(ctx.exception), expected)
        self.assertNotIn(FAKE_KEY, str(ctx.exception))

    def test_empty_input_shows_message_and_no_api_call(self):
        with mock.patch("builtins.input", side_effect=["", "room monitor"]), mock.patch("main.get_recommendation", return_value="ESP32") as rec, mock.patch("builtins.print") as shown:
            main.main()
        self.assertIn(errors.EMPTY_INPUT, [c.args[0] for c in shown.call_args_list if c.args])
        rec.assert_called_once_with("room monitor")

    def test_spaces_only_input_does_not_call_api(self):
        with mock.patch("microassist.recommender.genai.Client") as client:
            with self.assertRaises(errors.MicroAssistError) as ctx:
                recommender.get_recommendation("    ")
        self.assertEqual(str(ctx.exception), errors.EMPTY_INPUT)
        client.assert_not_called()

    def test_missing_api_key(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(errors.MicroAssistError) as ctx:
                recommender.get_recommendation("room monitor")
        self.assertEqual(str(ctx.exception), errors.MISSING_API_KEY)

    def test_connection_failure(self):
        self.check_message(httpx.ConnectError("no internet " + FAKE_KEY), errors.CONNECTION_FAILED)

    def test_timeout(self):
        self.check_message(httpx.ReadTimeout("too slow " + FAKE_KEY), errors.TIMED_OUT)

    def test_service_error(self):
        self.check_message(genai_errors.APIError(400, {"error": {"message": "bad key " + FAKE_KEY}}), errors.SERVICE_ERROR)

    def test_empty_ai_response(self):
        for reply in ("", "   "):
            with self.subTest(reply=repr(reply)):
                with mock.patch("microassist.recommender.genai.Client", return_value=fake_client(reply=reply)):
                    with self.assertRaises(errors.MicroAssistError) as ctx:
                        recommender.get_recommendation("room monitor")
                self.assertEqual(str(ctx.exception), errors.EMPTY_RESPONSE)

    def test_error_is_shown_without_traceback(self):
        with mock.patch("builtins.input", return_value="room monitor"), mock.patch("main.get_recommendation", side_effect=errors.MicroAssistError(errors.CONNECTION_FAILED)), mock.patch("builtins.print") as shown:
            main.main()
        self.assertIn(errors.CONNECTION_FAILED, " ".join(str(c.args[0]) for c in shown.call_args_list if c.args))

    def test_valid_request_still_works(self):
        for reply in ("Recommended: ESP32", "What is your power budget and required operating voltage?"):
            with self.subTest(reply=reply):
                with mock.patch("microassist.recommender.genai.Client", return_value=fake_client(reply=reply)):
                    self.assertEqual(recommender.get_recommendation("room monitor with Wi-Fi"), reply)

if __name__ == "__main__":
    unittest.main()
