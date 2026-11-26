"""SCRUM-37: tests for the verification check (SCRUM-17). Example AI answers
are used, so no real API calls are made.
"""
import unittest
from unittest import mock

import main
from microassist import verifier

GOOD = ("1. Recommended microcontroller or board\nESP32 (ESP32-WROOM-32) on an ESP32-DevKitC.\n"
        "2. Reasons: dual-core 240 MHz, 520 KB SRAM and 4 MB flash, with Wi-Fi and Bluetooth.")
INVENTED = "I recommend the ESP32-Z9 at 300 MHz. The STM32F999 is another option."


class TestVerify(unittest.TestCase):

    def test_known_parts_are_verified(self):
        result = verifier.verify(GOOD)
        self.assertIn("ESP32 (ESP32-WROOM-32)", [db for _, db in result["verified"]])
        self.assertEqual(result["unverified_parts"], [])
        self.assertEqual(result["unverified_specs"], [])

    def test_invented_parts_are_unverified(self):
        result = verifier.verify(INVENTED)
        self.assertEqual(result["unverified_parts"], ["ESP32-Z9", "STM32F999"])

    def test_wrong_clock_and_memory_are_unverified(self):
        result = verifier.verify("Use an Arduino Uno (ATmega328P) at 48 MHz with 64 KB flash and 2 KB RAM.")
        self.assertEqual(result["unverified_specs"], ["48 MHz", "64 KB"])

    def test_board_names_are_matched_to_their_chip(self):
        result = verifier.verify("Try the Arduino Nano ESP32, a Raspberry Pi Pico W or a Teensy 4.1.")
        self.assertEqual([db for _, db in result["verified"]],
                         ["ESP32-S3", "Raspberry Pi Pico W (RP2040 + CYW43439)", "NXP i.MX RT1062"])

    def test_part_not_in_database_is_unverified(self):
        self.assertIn("Arduino Due", verifier.verify("The Arduino Due is an option.")["unverified_parts"])

    def test_family_names_and_words_are_ignored(self):
        result = verifier.verify("Any ESP32-based board works; the STM32 family is also especially good.")
        self.assertEqual(result["unverified_parts"], [])

    def test_answer_without_parts(self):
        result = verifier.verify("Selection pending clarification. Which sensor do you use?")
        self.assertEqual(result, {"verified": [], "unverified_parts": [], "unverified_specs": []})


class TestReport(unittest.TestCase):

    def test_report_warns_and_suggests_datasheet(self):
        report = verifier.format_report(verifier.verify(INVENTED))
        self.assertIn("UNVERIFIED part: ESP32-Z9", report)
        self.assertIn("UNVERIFIED specification: 300 MHz", report)
        self.assertIn("official datasheet", report)

    def test_report_for_fully_verified_answer(self):
        report = verifier.format_report(verifier.verify(GOOD))
        self.assertIn("Verified in database: ESP32 (ESP32-WROOM-32)", report)
        self.assertIn("All named parts and clock/memory values match the database.", report)
        self.assertNotIn("UNVERIFIED", report)


class TestMainShowsVerification(unittest.TestCase):

    def run_main(self, answer):
        with mock.patch("builtins.input", return_value="weather station"), \
                mock.patch("main.load_dotenv"), \
                mock.patch("main.route", return_value="selection"), \
                mock.patch("main.get_recommendation", return_value=answer), \
                mock.patch("builtins.print") as shown:
            main.main()
        return "\n".join(str(c.args[0]) for c in shown.call_args_list if c.args)

    def test_verification_is_printed_after_recommendation(self):
        printed = self.run_main(INVENTED)
        self.assertLess(printed.index(INVENTED), printed.index("--- Verification"))
        self.assertIn("UNVERIFIED part: ESP32-Z9", printed)

    def test_debugging_answers_are_not_verified(self):
        with mock.patch("builtins.input", return_value="my board resets"), \
                mock.patch("main.load_dotenv"), \
                mock.patch("main.route", return_value="debugging"), \
                mock.patch("main.get_debug_help", return_value="Check the power supply."), \
                mock.patch("builtins.print") as shown:
            main.main()
        printed = "\n".join(str(c.args[0]) for c in shown.call_args_list if c.args)
        self.assertNotIn("--- Verification", printed)


if __name__ == "__main__":
    unittest.main()