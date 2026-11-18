# Prompt Evaluation: debugger_v1 (SCRUM-23)

**Prompt file:** `prompts/debugger_v1.md`
**Tested by:** Hammad Siddiqui
**Date:** 18 Nov 2026
**Model:** gemini-3.8-flash (system instruction = debugger_v1.md)

**How it was run:** Test 1 was first run in Google AI Studio (screenshots below). AI Studio then stopped being usable for the remaining tests (see Notes), so all three tests were run through the real debugging agent, `microassist/debugger.py` `get_debug_help()`, which sends the user text to gemini-3.8-flash with `prompts/debugger_v1.md` as the system instruction. The full response for each test is saved in `docs/test-results/sprint2/debugger-0N.md`.

## Acceptance criteria being checked (SCRUM-14)
1. The user can describe a symptom or paste an error message.
2. The response lists at least two likely causes.
3. Each cause includes a suggested check or fix.
4. When information is missing, the response asks for the needed details.

## Test cases

| # | Input given to the prompt | AC1 | AC2 (2+ causes) | AC3 (check/fix each) | AC4 (asks for missing info) | Pass/Fail | Notes |
|---|---|---|---|---|---|---|---|
| 1 | My ESP32 restarts every time I switch on the DC motor. | Yes | Yes | Yes | Yes | Pass | 2 causes (brownout from motor inrush current, inductive kickback/noise), each with Why/Check/Fix. Asks 3 questions (power source, motor driver, serial monitor message). Safety note about never driving a motor from a GPIO pin. 246 words. Same result in AI Studio. |
| 2 | Arduino IDE shows: `avrdude: stk500_recv(): programmer is not responding` | Yes | Yes | Yes | Yes | Pass | Pasted error message understood. 3 causes (wrong port/board, hardware on pins 0/1, charge-only cable or missing CH340/CP2102 driver), each with Why/Check/Fix. Asks 3 questions (board model, wiring on pins 0/1, whether a port appears). 290 words, close to the 300 limit. |
| 3 | My DHT11 sensor always reads 0. | Yes | Yes | Yes | Yes | Pass | 2 causes (missing pull-up resistor/wrong data pin, reading faster than every 2 s), each with Why/Check/Fix. Asks for board, 3-pin vs 4-pin sensor, and the code. 237 words. |

Mark each column with Yes / No.

## Result
3 of 3 passed. All responses used the four required headings, stayed under 300 words and asked focused follow-up questions. Weak points: test 3 says that reading the DHT11 too fast can give "cached zero values", which is stated more confidently than it should be (libraries usually return an error/NaN), and test 2 was only just under the word limit. These are minor, so no v2 is needed now; a v2 could tell the model to say "may" when a cause depends on the library used.

## Notes on the testing (honest record)
- **AI Studio problem:** in the AI Studio chat used for testing, test 2 was sent twice by mistake and the two answers were streamed into one reply, so the text was garbled (`aistudio-debugger-02-garbled-*.jpg`). This was a problem with the browser session, not the prompt. The free AI Studio quota then ran out, so the tests were finished through `debugger.py` instead.
- **Timeout:** on 18 Nov Gemini was overloaded (503 "high demand" and 504 "deadline exceeded" errors). `debugger.py` waits 30 s (`TIMEOUT_MS`); for this evaluation only, the test script raised this to 120 s. The prompt, model and code path were otherwise unchanged.
- **Bugs found while testing (outside SCRUM-23, reported to the team):**
  - `requirements.txt` does not list `httpx`, but `microassist/debugger.py` imports it, so `py -m unittest` fails on a fresh install with `No module named 'httpx'`.
  - When Google takes longer than the timeout, `debugger.py` crashes with a traceback (`httpx2.ReadTimeout`) instead of showing the friendly "timed out" message, because it catches `httpx.TimeoutException` but the current google-genai library uses `httpx2`.

## Screenshots
- Test 1 in AI Studio: `docs/test-results/sprint2/aistudio-debugger-01-a.jpg`, `aistudio-debugger-01-b.jpg`, `aistudio-debugger-01-c.jpg`
- Test 2 garbled AI Studio run (tooling problem, see Notes): `aistudio-debugger-02-garbled-a.jpg`, `aistudio-debugger-02-garbled-b.jpg`
- Full responses from `debugger.py`: `docs/test-results/sprint2/debugger-01.md`, `debugger-02.md`, `debugger-03.md`
