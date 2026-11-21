# Routing Evaluation v1 (SCRUM-29)

**What is tested:** the router agent in the full app (`py main.py`)
**Tested by:** Hammad Siddiqui
**Date:** 21 Nov 2026
**Model:** gemini-3.6-flash (set with the app's `MICROASSIST_MODEL` setting; see Notes for why not gemini-3.8-flash)

## Acceptance criteria being checked (SCRUM-15)
1. Microcontroller selection requests are sent to the recommendation agent.
2. Debugging requests are sent to the debugging agent.
3. Unclear requests receive a clarification question.
4. The chosen agent is shown with the response.

## Test cases

| # | Request typed into MicroAssist | Expected agent | Agent shown | Correct? |
|---|---|---|---|---|
| 1 | I want to build a weather station with Wi-Fi. Which board should I use? | Recommendation | Recommendation agent | Yes |
| 2 | Which microcontroller is best for a battery-powered step counter with Bluetooth? | Recommendation | Recommendation agent | Yes |
| 3 | I need a cheap board to control 4 servo motors for a robot arm. | Recommendation | Recommendation agent | Yes |
| 4 | My ESP32 keeps restarting when the motor turns on. | Debugging | Debugging agent | Yes |
| 5 | Arduino upload fails with "programmer is not responding". | Debugging | Debugging agent | Yes |
| 6 | My LCD shows only black boxes. | Debugging | Debugging agent | Yes |
| 7 | hello | Unclear | MicroAssist clarification question | Yes |
| 8 | Arduino | Unclear | MicroAssist clarification question | Yes |
| 9 | What is the weather today? | Unclear | MicroAssist clarification question | Yes |

## Result
9 of 9 routed correctly. All three selection requests went to the recommendation agent (AC1), all three debugging requests went to the debugging agent (AC2), and all three unclear requests ("hello", "Arduino", an off-topic weather question) got the clarification question (AC3). Every response showed the chosen agent in brackets (`[Recommendation agent]`, `[Debugging agent]` or `[MicroAssist]`) before the answer (AC4). All four SCRUM-15 acceptance criteria pass.

## Notes on the testing (honest record)
- **Why not gemini-3.8-flash:** on 20-21 Nov gemini-3.8-flash was heavily overloaded. With no timeout, a one-word test request took 710 s (about 12 minutes) to answer; with the app's limits (15 s for the router, 30 s for the agents) every request failed with 503 "high demand" or 504 "deadline exceeded". The key then also hit its free daily quota for that model (429). gemini-3.6-flash was the closest Flash model that responded, so the evaluation was run with `MICROASSIST_MODEL=gemini-3.6-flash`, a setting the app already supports (`.env.example`). Request 9 was run with a second free-tier key (from another Google account) after the first key's daily gemini-3.6-flash quota ran out; same model and settings. The router code and the prompts (`prompts/router_v1.md`, `recommender_v1.md`, `debugger_v1.md`) were not changed.
- **Misleading error message:** whenever Google fails (overload, timeout or quota), the app prints "Google AI returned an error. Check that your API key is correct, or try again later." The key was valid each time, so this message sends users in the wrong direction. Suggest a separate message for 503/504 ("Google AI is busy, try again in a minute") and for 429 ("daily limit reached").
- **Router timeout:** the router gives Google only 15 s. Under load this is too short; a retry with backoff, or a longer timeout, would make routing more reliable.

## Screenshots
One VS Code terminal screenshot per request, each showing the request and the agent label:
`docs/test-results/sprint2/route-01.png` … `route-09.png`.
The exact terminal text of each run is also saved as `route-01.txt` … `route-09.txt`.
