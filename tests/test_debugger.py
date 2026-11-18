"""SCRUM-25: tests for the debugging agent (SCRUM-14).

A fake Google AI client is used, so no internet or real API key is needed.
"""
import unittest
from types import SimpleNamespace
from unittest import mock

import httpx
from google.genai import errors as genai_errors

import errors
from microassist import debugger

FAKE_KEY = "test-key-12345"
PROBLEM = "My ESP32 restarts every time I switch on the DC motor."


def fake_client(reply=None, error=None):
    client = mock.MagicMock()
    if error is not None:
        client.models.generate_content.side_effect = error
    else:
        client.models.generate_content.return_value = SimpleNamespace(text=reply)
    return client


class TestDebugger(unittest.TestCase):

    def setUp(self):
        patch_env = mock.patch.dict("os.environ", {"GEMINI_API_KEY": FAKE_KEY}, clear=True)
        patch_env.start()
        self.addCleanup(patch_env.stop)
        self.client = fake_client(reply="1. Problem summary ...")
        patch_client = mock.patch("microassist.debugger.genai.Client", return_value=self.client)
        self.client_class = patch_client.start()
        self.addCleanup(patch_client.stop)

    def sent(self):
        """What our code sent to Google AI."""
        return self.client.models.generate_content.call_args.kwargs

    def error_message(self, error):
        with mock.patch("microassist.debugger.genai.Client", return_value=fake_client(error=error)):
            with self.assertRaises(errors.MicroAssistError) as ctx:
                debugger.get_debug_help(PROBLEM)
        self.assertNotIn(FAKE_KEY, str(ctx.exception))
        return str(ctx.exception)

    def test_debugging_prompt_file_is_loaded(self):
        prompt = debugger.load_prompt()
        self.assertIn("debugging agent", prompt)
        self.assertIn("at least two likely causes", prompt)

    def test_debugging_prompt_is_sent_as_system_instruction(self):
        debugger.get_debug_help(PROBLEM)
        self.assertEqual(self.sent()["config"].system_instruction, debugger.load_prompt())

    def test_problem_is_sent_unchanged(self):
        debugger.get_debug_help(PROBLEM)
        self.assertEqual(self.sent()["contents"], PROBLEM)

    def test_api_key_comes_from_environment(self):
        debugger.get_debug_help(PROBLEM)
        self.client_class.assert_called_once_with(api_key=FAKE_KEY)

    def test_answer_is_returned(self):
        self.assertEqual(debugger.get_debug_help(PROBLEM), "1. Problem summary ...")

    def test_empty_problem_makes_no_api_call(self):
        for text in ("", "    "):
            with self.subTest(text=repr(text)):
                with self.assertRaises(errors.MicroAssistError) as ctx:
                    debugger.get_debug_help(text)
                self.assertEqual(str(ctx.exception), errors.EMPTY_INPUT)
        self.client_class.assert_not_called()

    def test_missing_api_key(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(errors.MicroAssistError) as ctx:
                debugger.get_debug_help(PROBLEM)
        self.assertEqual(str(ctx.exception), errors.MISSING_API_KEY)

    def test_connection_failure(self):
        self.assertEqual(self.error_message(httpx.ConnectError("offline " + FAKE_KEY)), errors.CONNECTION_FAILED)

    def test_timeout(self):
        self.assertEqual(self.error_message(httpx.ReadTimeout("slow " + FAKE_KEY)), errors.TIMED_OUT)

    def test_service_error(self):
        error = genai_errors.APIError(400, {"error": {"message": "bad key " + FAKE_KEY}})
        self.assertEqual(self.error_message(error), errors.SERVICE_ERROR)

    def test_empty_ai_response(self):
        with mock.patch("microassist.debugger.genai.Client", return_value=fake_client(reply="  ")):
            with self.assertRaises(errors.MicroAssistError) as ctx:
                debugger.get_debug_help(PROBLEM)
        self.assertEqual(str(ctx.exception), errors.EMPTY_RESPONSE)


if __name__ == "__main__":
    unittest.main()
