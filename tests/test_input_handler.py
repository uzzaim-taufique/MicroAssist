"""SCRUM-10: command-line requirements, adapted to the merged main.py API."""
import unittest
from unittest import mock
import main

class TestInputHandler(unittest.TestCase):
    def run_input(self, text):
        with mock.patch("builtins.input", return_value=text) as entered, mock.patch("main.get_recommendation", return_value="ESP32") as rec, mock.patch("main.load_dotenv"), mock.patch("builtins.print"):
            main.main()
        return entered, rec

    def test_prompt_asks_for_project_requirements(self):
        entered, _ = self.run_input("robot")
        self.assertIn("project requirements", entered.call_args.args[0])

    def test_submitted_text_is_captured(self):
        _, rec = self.run_input("room monitor")
        rec.assert_called_once_with("room monitor")

    def test_leading_and_trailing_spaces_removed(self):
        _, rec = self.run_input("   room monitor   ")
        rec.assert_called_once_with("room monitor")

    def test_internal_wording_and_punctuation_unchanged(self):
        text = "A room monitor,  with a temperature sensor & Wi-Fi!"
        _, rec = self.run_input("  " + text + "  ")
        rec.assert_called_once_with(text)

    def test_requirements_passed_to_recommendation_function(self):
        _, rec = self.run_input("Wi-Fi room monitor")
        rec.assert_called_once_with("Wi-Fi room monitor")

if __name__ == "__main__":
    unittest.main()
