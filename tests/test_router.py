"""SCRUM-28: tests for the router agent and for sending each request to the
right agent (SCRUM-15). No real API calls are made.
"""
import unittest
from types import SimpleNamespace
from unittest import mock

import httpx

import errors
import main
from microassist import router

FAKE_KEY = "test-key-12345"


def fake_client(reply=None, error=None):
    client = mock.MagicMock()
    if error is not None:
        client.models.generate_content.side_effect = error
    else:
        client.models.generate_content.return_value = SimpleNamespace(text=reply)
    return client


class TestRouter(unittest.TestCase):

    def setUp(self):
        patch_env = mock.patch.dict("os.environ", {"GEMINI_API_KEY": FAKE_KEY}, clear=True)
        patch_env.start()
        self.addCleanup(patch_env.stop)

    def route_with_reply(self, reply):
        client = fake_client(reply=reply)
        with mock.patch("microassist.router.genai.Client", return_value=client):
            label = router.route("some request")
        return label, client

    def test_selection_request(self):
        self.assertEqual(self.route_with_reply("selection")[0], router.SELECTION)

    def test_debugging_request(self):
        self.assertEqual(self.route_with_reply("debugging")[0], router.DEBUGGING)

    def test_unclear_request(self):
        self.assertEqual(self.route_with_reply("unclear")[0], router.UNCLEAR)

    def test_reply_with_extra_spaces_case_or_punctuation(self):
        for reply in ("  Selection\n", "DEBUGGING.", "debugging - the user has an error"):
            with self.subTest(reply=reply):
                self.assertIn(self.route_with_reply(reply)[0], (router.SELECTION, router.DEBUGGING))

    def test_unexpected_reply_is_treated_as_unclear(self):
        for reply in ("", None, "ESP32", "I think you should buy an Arduino"):
            with self.subTest(reply=reply):
                self.assertEqual(self.route_with_reply(reply)[0], router.UNCLEAR)

    def test_router_prompt_is_used(self):
        _, client = self.route_with_reply("selection")
        config = client.models.generate_content.call_args.kwargs["config"]
        self.assertEqual(config.system_instruction, router.load_prompt())
        self.assertIn("exactly one word", router.load_prompt())

    def test_empty_request_makes_no_api_call(self):
        with mock.patch("microassist.router.genai.Client") as client_class:
            with self.assertRaises(errors.MicroAssistError):
                router.route("   ")
        client_class.assert_not_called()

    def test_ai_failure_gives_friendly_message(self):
        with mock.patch("microassist.router.genai.Client", return_value=fake_client(error=httpx.ConnectError("x"))):
            with self.assertRaises(errors.MicroAssistError) as ctx:
                router.route("my board is broken")
        self.assertEqual(str(ctx.exception), errors.CONNECTION_FAILED)


class TestMainSendsToRightAgent(unittest.TestCase):

    def run_main(self, label):
        with mock.patch("builtins.input", return_value="my request"), \
                mock.patch("main.load_dotenv"), \
                mock.patch("main.route", return_value=label), \
                mock.patch("main.get_recommendation", return_value="REC") as rec, \
                mock.patch("main.get_debug_help", return_value="DEBUG") as dbg, \
                mock.patch("builtins.print") as shown:
            main.main()
        printed = [str(c.args[0]) for c in shown.call_args_list if c.args]
        return rec, dbg, printed

    def test_selection_goes_to_recommendation_agent(self):
        rec, dbg, printed = self.run_main(router.SELECTION)
        rec.assert_called_once_with("my request")
        dbg.assert_not_called()
        self.assertTrue(any("[Recommendation agent]" in p for p in printed))

    def test_debugging_goes_to_debugging_agent(self):
        rec, dbg, printed = self.run_main(router.DEBUGGING)
        dbg.assert_called_once_with("my request")
        rec.assert_not_called()
        self.assertTrue(any("[Debugging agent]" in p for p in printed))

    def test_unclear_gets_clarification_question(self):
        rec, dbg, printed = self.run_main(router.UNCLEAR)
        rec.assert_not_called()
        dbg.assert_not_called()
        self.assertIn(router.CLARIFICATION, printed)


if __name__ == "__main__":
    unittest.main()