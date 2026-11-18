# Debugger test 3 (SCRUM-23)

- Run: 2026-11-18 10:34 via microassist/debugger.py get_debug_help()
- Model: gemini-3.8-flash
- Prompt: prompts/debugger_v1.md

## Input

My DHT11 sensor always reads 0.

## Response

### 1. Problem summary
Your DHT11 temperature and humidity sensor consistently returns a value of 0 instead of valid measurements.

### 2. Likely causes and fixes

* **Missing pull-up resistor or incorrect wiring on the data line**
  * *Why:* The DHT11 uses a single-wire protocol that requires a 4.7kΩ to 10kΩ pull-up resistor between the data pin and VCC (unless using a 3-pin breakout module that includes one). Without it, the line cannot signal properly.
  * *Check:* Verify if your sensor is a bare 4-pin component without a resistor, and check that the data wire matches the digital pin defined in your code.
  * *Fix:* Wire a 4.7kΩ–10kΩ resistor between VCC and Data, or correct the pin assignment in your sketch.

* **Sampling the sensor too fast**
  * *Why:* The DHT11 is slow and requires 1 to 2 seconds between readings. Reading it faster causes communication errors or cached zero values.
  * *Check:* Look at your code's main loop to see how frequently you call the read function.
  * *Fix:* Add a delay of at least 2000 milliseconds (2 seconds) between sensor readings.

### 3. Information needed
1. Which microcontroller board are you using (e.g., Arduino Uno, ESP32)?
2. Is your DHT11 a 3-pin module or a bare 4-pin sensor?
3. Could you share the code you are using to read the sensor?

### 4. Safety notes
Double-check your power connections. Reversing VCC and GND, or shorting them, will permanently damage the DHT11 sensor and potentially your microcontroller board.
