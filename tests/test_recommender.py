"""SCRUM-19: tests for the Google AI recommendation integration (SCRUM-7).

A fake Google AI client is used, so no internet or real API key is needed.
"""
import unittest
from types import SimpleNamespace
from unittest import mock

from microassist import recommender

FAKE_KEY = "test-key-12345"
REQUIREMENTS = ("I want to build a room-monitoring system with a temperature "
                "sensor and Wi-Fi connectivity.")


class TestRecommender(unittest.TestCase):

    def setUp(self):
        # Use a fake key and never the real one.
        patch_env = mock.patch.dict("os.environ", {"GEMINI_API_KEY": FAKE_KEY}, clear=True)
        patch_env.start()
        self.addCleanup(patch_env.stop)

        # A pretend Google AI client that always answers with a fixed text.
        self.fake_client = mock.MagicMock()
        self.fake_client.models.generate_content.return_value = SimpleNamespace(
            text="Recommended microcontroller: ESP32")
        patch_client = mock.patch("microassist.recommender.genai.Client",
                                  return_value=self.fake_client)
        self.client_class = patch_client.start()
        self.addCleanup(patch_client.stop)

    def sent(self):
        """What our code sent to Google AI."""
        return self.fake_client.models.generate_content.call_args.kwargs

    def test_prompt_file_is_loaded(self):
        prompt = recommender.load_prompt()
        self.assertIn("MicroAssist", prompt)

    def test_requirements_are_sent_unchanged(self):
        recommender.get_recommendation(REQUIREMENTS)
        self.assertEqual(self.sent()["contents"], REQUIREMENTS)

    def test_versioned_instruction_prompt_is_sent(self):
        recommender.get_recommendation(REQUIREMENTS)
        self.assertEqual(self.sent()["config"].system_instruction, recommender.load_prompt())

    def test_api_key_comes_from_environment(self):
        recommender.get_recommendation(REQUIREMENTS)
        self.assertEqual(self.client_class.call_args.kwargs["api_key"], FAKE_KEY)

    def test_default_model_is_used(self):
        recommender.get_recommendation(REQUIREMENTS)
        self.assertEqual(self.sent()["model"], recommender.DEFAULT_MODEL)

    def test_ai_answer_is_returned(self):
        answer = recommender.get_recommendation(REQUIREMENTS)
        self.assertIn("ESP32", answer)


if __name__ == "__main__":
    unittest.main()
