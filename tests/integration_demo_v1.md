# MicroAssist integration demo: Sprint 1

- Jira: SCRUM-12 (Google AI recommendation integration) and SCRUM-9 (command-line input flow), under stories SCRUM-7 and SCRUM-6
- Branch: `SCRUM-12-google-ai-integration`
- Run by: Umar Yasir, 21 October 2026, Windows 11, Python 3.14.4, google-genai 2.32.0
- Command: `python main.py`, API key loaded from a local `.env` file (not committed)
- Model: `gemini-3.5-flash-lite`, set with `MICROASSIST_MODEL`. The default `gemini-3.8-flash` and `gemini-3.7-flash` both returned `503 UNAVAILABLE` ("high demand") at the time of testing. `gemini-2.5-flash` returned `404 NOT_FOUND` (no longer available to new users).

## Summary

| # | Input | What it checks | Result |
| --- | --- | --- | --- |
| 1 | SCRUM-6 example input | Input captured, sent with `prompts/recommender_v1.md` to Google AI, response printed in the terminal | Pass |
| 2 | Same input with 3 spaces before and after | Leading and trailing spaces trimmed, request still works | Pass |
| 3 | `I need a microcontroller for my project.` | Clarification questions are displayed when information is missing | Pass |

## Observations

- Runs 1 and 2 used the same requirements but recommended different boards (ESP32 NodeMCU, then Raspberry Pi Pico W). Both meet the requirements. This shows the AI output is not deterministic, which should be considered in later prompt testing.
- Run 2 printed Markdown bold markers (`**`) as plain text in the terminal. Readable, but formatting could be improved in a later sprint.
- Raw tracebacks were shown for the 503 and 404 errors above. Friendly error messages are the scope of SCRUM-8.

## Run 1: SCRUM-6 example input

```text
MicroAssist - microcontroller recommendation assistant
Describe your project requirements: I want to build a room-monitoring system with a temperature sensor and Wi-Fi connectivity.

Asking Google AI...

1. Recommended microcontroller or board
ESP32 NodeMCU development board.

2. Reasons for the recommendation
- Meets your core needs with integrated Wi-Fi for remote monitoring.
- Provides ample processing power and GPIO pins to easily read a temperature sensor (such as a DHT22 or I2C sensor).
- Low cost and widely available for student projects.
- Supports popular IDEs like Arduino for straightforward programming.

3. Assumptions or clarification needed
- Assumption: You will power the board via USB rather than battery.
- Question 1: Do you plan to display the temperature locally (e.g., on an LCD screen), or will all data be sent exclusively over Wi-Fi?
- Question 2: What specific temperature sensor do you plan to use?

4. Limitations and specifications to verify
- Operating voltage: Typically 3.3V logic levels. Be careful not to apply 5V directly to the GPIO pins.
- GPIO availability: Check that enough pins remain free if you add extra peripherals.
- Power consumption: Wi-Fi drawing current spikes can cause resets if your power supply is unstable.
- Check the exact manufacturer datasheet or pinout diagram for your specific module variant before wiring.

*Treat this recommendation as guidance requiring verification before purchasing or connecting hardware.*
```

## Run 2: input with surrounding spaces

```text
MicroAssist - microcontroller recommendation assistant
Describe your project requirements:    I want to build a room-monitoring system with a temperature sensor and Wi-Fi connectivity.  

Asking Google AI...

1. Recommended microcontroller or board
**Raspberry Pi Pico W**

2. Reasons for the recommendation
- **Connectivity:** Features built-in Wi-Fi via the Infineon CYW43439 wireless chip, meeting your wireless requirement.
- **Sensor Interfaces:** Supports standard protocols like I2C, SPI, and analog pins, making it easy to connect common temperature sensors like the DHT22, BME280, or LM35.
- **Processing Needs:** The RP2040 dual-core ARM Cortex-M0+ processor handles reading sensors and sending data over Wi-Fi with ease.
- **Budget:** It is very affordable and widely available for student projects.

3. Assumptions or clarification needed
- **Assumption:** You plan to power the board via USB or a stable 5V source, rather than strict battery-saving low-power modes.
- **Question:** How do you plan to power the system (USB or battery)?
- **Question:** Do you have a preferred programming language (MicroPython, C/C++, or Arduino IDE)?

4. Limitations and specifications to verify
- **Operating Voltage:** The board logic runs at 3.3V; check that your chosen temperature sensor is compatible.
- **GPIO Availability:** Verify that enough pins remain free if you plan to add displays or extra sensors later.
- **Memory:** The Pico W has 2MB of onboard flash memory, which is sufficient for basic Wi-Fi stacks and sensor code, but check constraints if you plan to host a local web server.
```

## Run 3: insufficient information

```text
MicroAssist - microcontroller recommendation assistant
Describe your project requirements: I need a microcontroller for my project.

Asking Google AI...

1. Recommended microcontroller or board
Selection pending clarification.

2. Reasons for the recommendation
To choose the right microcontroller, I need to understand what your project involves. Different projects require different processing power, memory, power consumption, and physical sizes.

3. Assumptions or clarification needed
- What is your project trying to do, and what sensors, actuators, or displays will you connect?
- Do you need wireless connectivity (such as Wi-Fi or Bluetooth), and what is your power source (battery or USB)?

4. Limitations and specifications to verify
Once you share your project details, you will need to check the official manufacturer documentation for the suggested board's exact specifications. Always verify operating voltages, current limits on GPIO pins, available communication interfaces (like I2C, SPI, and UART), and physical dimensions before purchasing or connecting hardware.
```
