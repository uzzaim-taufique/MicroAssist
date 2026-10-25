# SCRUM-8 Error Handling Test Log

Tester: Abdullah
Date: 25 Oct 2026
Code version: main branch on 25 Oct 2026

## Test 1: Empty input

* What I did: Started the app and pressed Enter without typing anything
* Expected: Shows "Please enter your project requirements." and asks again (no AI call)
* Actual result: Empty input displayed the error message and asked for input again.
* Pass/Fail: Pass
* Screenshot: screenshots/01-empty.png.jpeg

## Test 2: Only spaces

* What I did: Typed 3 spaces, then pressed Enter
* Expected: Same message as Test 1 and asks again
* Actual result: Entering only three spaces displayed the error message and asked for input again.
* Pass/Fail: Pass
* Screenshot: screenshots/02-spaces.png.jpeg

## Test 3: Valid request

* What I did: Typed: I want to build a room-monitoring system with a temperature sensor and Wi-Fi connectivity.
* Expected: Shows a microcontroller recommendation under 4 headings
* Actual result: The valid request was submitted, but Google AI returned an error about the API key or service.
* Pass/Fail: Fail
* Screenshot: screenshots/03-valid.png.jpeg

## Test 4: Missing API key

* What I did: Renamed .env to env\_backup, started the app, typed a valid request
* Expected: "\[MicroAssist] API key not found. Add GEMINI\_API\_KEY to your .env file and try again." No crash
* Actual result: The app displayed the API key not found message without crashing.
* Pass/Fail: Pass
* Screenshot: screenshots/04-no-key.png.jpeg

## Test 5: No internet

* What I did: Turned Wi-Fi off, started the app, typed a valid request
* Expected: "\[MicroAssist] Could not connect to Google AI. Check your internet connection and try again." No crash
* Actual result: The app displayed â€œCould not connect to Google AI. Check your internet connection and try again.â€ and returned to the command prompt without crashing.
* Pass/Fail: Pass
* Screenshot: screenshots/05-no-internet.png.jpeg

## Test 6: Wrong API key

* What I did: Changed one letter of the key in .env, started the app, typed a valid request
* Expected: "\[MicroAssist] Google AI returned an error. Check that your API key is correct, or try again later." No crash
* Actual result: The app displayed the expected API key error message without crashing.
* Pass/Fail: Pass
* Screenshot: screenshots/06-wrong-key.png.jpeg

## Summary

6 tests run, 5 passed, 1 failed.

