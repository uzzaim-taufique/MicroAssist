"""SCRUM-34: tests for the verified database, the search tool and function
calling (SCRUM-16). No real API calls are made.
"""
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from google import genai
from google.genai import types

from microassist import database, recommender

REQUIRED_FIELDS = {"id", "name", "manufacturer", "clock_mhz", "flash_kb", "ram_kb", "wifi",
                   "bluetooth", "adc", "logic_level_v", "aliases", "datasheet_source"}


class TempLogMixin:
    """Write the search log to a temporary folder instead of logs/."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.log_path = Path(folder.name) / "database_searches.jsonl"
        patch_log = mock.patch.object(database, "LOG_PATH", self.log_path)
        patch_log.start()
        self.addCleanup(patch_log.stop)
        database.SEARCH_LOG.clear()


class TestDatabaseFile(unittest.TestCase):

    def test_at_least_20_microcontrollers(self):
        self.assertGreaterEqual(len(database.load_database()), 20)

    def test_every_entry_has_the_key_specifications(self):
        for entry in database.load_database():
            with self.subTest(part=entry.get("id")):
                self.assertTrue(REQUIRED_FIELDS.issubset(entry))
                self.assertGreater(entry["flash_kb"], 0)
                self.assertGreater(entry["ram_kb"], 0)
                self.assertTrue(entry["clock_mhz"])
                self.assertTrue(entry["aliases"])

    def test_ids_are_unique(self):
        ids = [e["id"] for e in database.load_database()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_find_part_by_alias(self):
        self.assertEqual(database.find_part("Arduino Uno")["id"], "atmega328p")
        self.assertEqual(database.find_part("esp32 s3")["id"], "esp32-s3")
        self.assertIsNone(database.find_part("ESP32-Z9"))


class TestSearchTool(TempLogMixin, unittest.TestCase):

    def ids(self, **filters):
        return [r["id"] for r in database.search_microcontrollers(**filters)["results"]]

    def test_search_by_name(self):
        self.assertIn("rp2040", self.ids(name="RP2040"))

    def test_wifi_filter(self):
        for part in database.search_microcontrollers(needs_wifi=True, max_results=10)["results"]:
            self.assertTrue(part["wifi"])

    def test_bluetooth_filter(self):
        ids = self.ids(needs_bluetooth=True, max_results=10)
        self.assertIn("nrf52840", ids)
        self.assertNotIn("esp8266", ids)

    def test_memory_filters(self):
        for part in database.search_microcontrollers(min_flash_kb=512, min_ram_kb=128, max_results=10)["results"]:
            self.assertGreaterEqual(part["flash_kb"], 512)
            self.assertGreaterEqual(part["ram_kb"], 128)

    def test_logic_level_filter(self):
        for part in database.search_microcontrollers(logic_level_v=5, max_results=10)["results"]:
            self.assertEqual(part["logic_level_v"], 5.0)

    def test_max_results_is_limited(self):
        self.assertLessEqual(len(self.ids(max_results=50)), database.MAX_RESULTS)

    def test_no_match_returns_empty_list(self):
        self.assertEqual(database.search_microcontrollers(name="no such chip"), {"count": 0, "results": []})

    def test_searches_are_recorded(self):
        database.search_microcontrollers(needs_wifi=True, max_results=2)
        self.assertEqual(len(database.SEARCH_LOG), 1)
        self.assertTrue(database.SEARCH_LOG[0]["arguments"]["needs_wifi"])
        lines = self.log_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(json.loads(lines[0])["result_ids"], database.SEARCH_LOG[0]["result_ids"])


class TestRecommenderUsesTheTool(unittest.TestCase):

    def setUp(self):
        patch_env = mock.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True)
        patch_env.start()
        self.addCleanup(patch_env.stop)
        self.client = mock.MagicMock()
        self.client.models.generate_content.return_value = SimpleNamespace(text="ESP32")
        patch_client = mock.patch("microassist.recommender.genai.Client", return_value=self.client)
        patch_client.start()
        self.addCleanup(patch_client.stop)

    def test_search_tool_is_given_to_gemini(self):
        recommender.get_recommendation("weather station with Wi-Fi")
        config = self.client.models.generate_content.call_args.kwargs["config"]
        self.assertIn(database.search_microcontrollers, config.tools)

    def test_prompt_v2_is_used_and_mentions_the_tool(self):
        self.assertTrue(str(recommender.PROMPT_PATH).endswith("recommender_v2.md"))
        self.assertIn("search_microcontrollers", recommender.load_prompt())


class FakeGemini(BaseHTTPRequestHandler):
    """A pretend Gemini server: first it asks for the tool, then it answers."""
    requests = []

    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeGemini.requests.append(body)
        if len(FakeGemini.requests) == 1:
            parts = [{"functionCall": {"name": "search_microcontrollers",
                                       "args": {"needs_wifi": True, "max_results": 3}}}]
        else:
            parts = [{"text": "1. Recommended microcontroller or board\nESP32 (ESP32-WROOM-32)"}]
        reply = json.dumps({"candidates": [{"content": {"role": "model", "parts": parts},
                                            "finishReason": "STOP"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)


class TestFunctionCallingIntegration(TempLogMixin, unittest.TestCase):
    """Integration test: the real SDK runs our tool when Gemini asks for it."""

    def test_gemini_calls_the_tool_and_gets_database_results(self):
        FakeGemini.requests = []
        server = HTTPServer(("127.0.0.1", 0), FakeGemini)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.shutdown)
        with mock.patch.dict(os.environ, {"NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"}):
            client = genai.Client(api_key="test-key", http_options=types.HttpOptions(
                base_url=f"http://127.0.0.1:{server.server_port}"))
            answer = recommender.get_recommendation("weather station with Wi-Fi", client=client)

        self.assertIn("ESP32", answer)
        self.assertEqual(len(FakeGemini.requests), 2)       # question, then tool result
        self.assertEqual(len(database.SEARCH_LOG), 1)       # our function really ran
        sent_back = [p["functionResponse"] for c in FakeGemini.requests[1]["contents"]
                     for p in c["parts"] if "functionResponse" in p]
        results = sent_back[0]["response"]["result"]["results"]
        self.assertTrue(results and all(r["wifi"] for r in results))


if __name__ == "__main__":
    unittest.main()