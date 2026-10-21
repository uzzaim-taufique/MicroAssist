# MicroAssist prompt evaluation: recommender_v1

- Jira: SCRUM-13 (subtask of SCRUM-7, "Receive a justified microcontroller recommendation")
- Prompt tested: `prompts/recommender_v1.md` from branch `SCRUM-13-instruction-prompt` (commit 6cfa53b)
- Tool: Google AI Studio, prompt pasted as System instructions, new chat for each test
- Model: GEMINI FLASH 3.8
- Tested by: Umar Yasir, 21 October 2026

## Summary

| # | Test case (from SCRUM-7 Definition of Done) | Expected behaviour | Result |
| --- | --- | --- | --- |
| 1 | Wi-Fi project | Names a Wi-Fi capable board, explains connectivity and sensor interfaces | Pass |
| 2 | Simple project without wireless | Names a simple board, does not add unrequested wireless | Pass |
| 3 | Request with insufficient information | Does not guess a board, says "Selection pending clarification.", asks up to two questions | Pass |

All three responses used the four required headings in order and stayed under 250 words.

## Checks against SCRUM-7 acceptance criteria

| Acceptance criterion | Test 1 | Test 2 | Test 3 |
| --- | --- | --- | --- |
| Clearly names a recommended board when requirements are detailed | Yes (ESP32 DevKit) | Yes (Arduino Nano) | Not applicable, correctly withheld |
| Explains how it meets connectivity, sensor interface and processing needs | Yes, connectivity and sensors; processing only briefly | Yes | Not applicable |
| Asks for clarification or states assumptions when information is missing | Yes, assumptions plus 2 questions | Yes, assumption stated, no questions needed | Yes, 2 questions |
| Includes limitations and specifications to verify in official documentation | Yes | Yes | Yes, general checklist |

The criteria about sending requirements to Google AI from the application and showing the response in the terminal belong to SCRUM-12 (code) and are not tested here.

## Observations

- Test 1 labelled the answer "provisional" even though the input is the story's own detailed example. This is acceptable because it stated its assumptions, but a reviewer may want to decide whether this is desired.
- Test 3 asked two numbered questions, but each one combines two sub-questions. This is within the letter of the "up to two questions" rule but stretches it.
- Specific numbers given (14 digital I/O pins on the Nano, about 20 mA per pin, 500 mA supply for ESP32) were each paired with an instruction to verify them in the datasheet. No invented part numbers were seen.

## Test 1: Wi-Fi project

Input:

> I want to build a room-monitoring system with a temperature sensor and Wi-Fi connectivity.

Output:

```text
1. Recommended microcontroller or board

ESP32 Development Board (ESP32-WROOM-32 DevKit) — Provisional recommendation

2. Reasons for the recommendation

  - Integrated Wi-Fi: Built-in 2.4 GHz Wi-Fi allows easy data transmission to
    local servers or cloud dashboards without extra modules.
  - Sensor support: Provides hardware interfaces (I2C, SPI, UART, ADC)
    compatible with common temperature sensors like the DHT22, DS18B20, or
    BME280.
  - Beginner friendly: Large community support and ready-to-use libraries in the
    Arduino IDE make setup straightforward.

3. Assumptions or clarification needed

  - Assumptions: You will power the device via USB/mains electricity and connect
    via standard 2.4 GHz Wi-Fi.
  - Questions:
    1.  Will this project be powered by batteries or continuous USB/mains power?
    2.  Which specific temperature sensor (e.g., analog, I2C, or 1-Wire) do you
        plan to use?

4. Limitations and specifications to verify

  - Logic levels: The ESP32 uses 3.3 V logic. Its GPIO pins are not 5 V
    tolerant; check sensor voltage levels before connecting.
  - Power consumption: Wi-Fi radio activity causes brief current spikes; verify
    your power supply can deliver at least 500 mA.
  - Pinout differences: Board layouts vary by manufacturer. Check the official
    pinout diagram for your exact board variant to identify usable GPIOs (some
    pins are input-only or reserved for internal flash).
```

## Test 2: simple project without wireless

Input:

> I want to build a traffic light model with three LEDs and a push button for pedestrians, powered from a USB cable. It does not need any wireless connection.

Output:

```text
1. Recommended microcontroller or board

Arduino Nano (ATmega328P)

2. Reasons for the recommendation

  - GPIO needs: It provides 14 digital I/O pins, easily covering the 4 pins
    needed (3 for LEDs, 1 for the button).
  - Power: Runs directly from a standard 5V USB connection.
  - Ease of use: 5V logic levels make driving basic LEDs and reading simple push
    buttons straightforward without level shifters.
  - Form factor: Its compact, breadboard-friendly layout is well-suited for
    benchtop models.

3. Assumptions or clarification needed

  - Assumes you are using a standard 5V USB power supply (such as a PC port or
    phone charger).
  - No further clarifications are needed.

4. Limitations and specifications to verify

  - GPIO current limits: Check the ATmega328P datasheet for per-pin current
    limits (typically up to 20 mA recommended) and always include suitable
    current-limiting resistors for the LEDs.
  - USB connector type: Verify which USB port your specific Nano variant uses
    (Mini-B, Micro-USB, or USB-C) to ensure you have the correct cable.
  - Pinout and internal pull-ups: Verify the pinout diagram and enable the
    internal pull-up resistor in code if you wire the button to ground without
    an external resistor.
```

## Test 3: insufficient information

Input:

> I need a microcontroller for my project.

Output:

```text
1. Recommended microcontroller or board

Selection pending clarification.

2. Reasons for the recommendation

No project details were provided. A suitable microcontroller or development
board cannot be recommended without knowing your project's specific hardware
interfaces, processing demands, and connectivity requirements.

3. Assumptions or clarification needed

To help narrow down the best option, please answer these two questions:

1.  What sensors, displays, or actuators will you connect, and do you need
    wireless communication (such as Wi-Fi or Bluetooth)?
2.  How will the device be powered (battery or mains/USB), and which programming
    language do you plan to use (e.g., Arduino C++, MicroPython, or pure C)?

4. Limitations and specifications to verify

Before purchasing any hardware once selected, verify the following in the
official datasheet:

  - Operating voltage: Check whether the chip uses 3.3V or 5V logic to ensure
    compatibility with your sensors.
  - Pin count: Confirm there are enough free GPIO pins and dedicated hardware
    buses (I2C, SPI, UART, ADC).
  - Memory: Ensure flash memory and RAM are sufficient for your code and
    external libraries.
  - Power draw: Check active and sleep current if designing a battery-powered
    device.
```

## Review

- Reviewer: REVIEWER_NAME_HERE
- Review date: REVIEW_DATE_HERE
- Result: REVIEW_RESULT_HERE (approved, or changes requested with reasons)
