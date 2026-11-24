"""SCRUM-33: clear messages when Google AI is busy or the daily limit is reached.
 
Found in the Sprint 2 routing evaluation: 503/504/429 errors told the user to
check their API key, although the key was fine. No real API calls are made.
"""
import unittest
from unittest import mock
 
from google.genai import errors as genai_errors
 
import errors
from microassist import debugger, recommender, router
 
 
def api_error(code):
    return genai_errors.APIError(code, {"error": {"code": code, "message": "test"}})
 
 
class TestApiErrorMessage(unittest.TestCase):
 
    def test_daily_limit(self):
        self.assertEqual(errors.api_error_message(api_error(429)), errors.DAILY_LIMIT)
 
    def test_google_busy(self):
        for code in (500, 502, 503, 504):
            with self.subTest(code=code):
                self.assertEqual(errors.api_error_message(api_error(code)), errors.BUSY)
 
    def test_wrong_key_still_says_check_key(self):
        for code in (400, 401, 403):
            with self.subTest(code=code):
                self.assertEqual(errors.api_error_message(api_error(code)), errors.SERVICE_ERROR)
 
 
class TestAgentsUseTheRightMessage(unittest.TestCase):
 
    def setUp(self):
        patch_env = mock.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True)
        patch_env.start()
        self.addCleanup(patch_env.stop)
 
    def message(self, module, function, code):
        client = mock.MagicMock()
        client.models.generate_content.side_effect = api_error(code)
        with mock.patch(f"microassist.{module}.genai.Client", return_value=client):
            with self.assertRaises(errors.MicroAssistError) as ctx:
                function("my project")
        return str(ctx.exception)
 
    def test_recommender_busy(self):
        self.assertEqual(self.message("recommender", recommender.get_recommendation, 503), errors.BUSY)
 
    def test_debugger_busy(self):
        self.assertEqual(self.message("debugger", debugger.get_debug_help, 504), errors.BUSY)
 
    def test_router_daily_limit(self):
        self.assertEqual(self.message("router", router.route, 429), errors.DAILY_LIMIT)
 
 
if __name__ == "__main__":
    unittest.main()
