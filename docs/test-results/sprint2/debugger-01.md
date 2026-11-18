# Debugger test 1 (SCRUM-23)

- Run: 2026-11-18 10:33 via microassist/debugger.py get_debug_help()
- Model: gemini-3.8-flash
- Prompt: prompts/debugger_v1.md

## Input

My ESP32 restarts every time I switch on the DC motor.

## Response

### 1. Problem summary
Your ESP32 reboots immediately whenever your DC motor is switched on.

### 2. Likely causes and fixes

* **Voltage drop (Brownout):**
  * **Why:** Motors draw high inrush current when starting, causing the power supply voltage to dip below the ESP32's minimum operating voltage.
  * **Check:** Check if the motor and ESP32 share the same power supply, or check if the ESP32 serial monitor prints a "Brownout detector was triggered" message.
  * **Fix:** Power the motor using a separate power supply (connect their ground pins together), or add a large capacitor (e.g., 470 µF or 1000 µF) across the power rail.

* **Inductive kickback and electrical noise:**
  * **Why:** Switching inductive loads like motors generates reverse voltage spikes and electrical noise that reset the microcontroller.
  * **Check:** Check whether you have a flyback diode across the motor terminals.
  * **Fix:** Connect a rectifier diode (such as a 1N4001 or 1N4007) across the motor terminals in reverse bias (cathode to positive, anode to ground) to absorb voltage spikes.

### 3. Information needed
* What power source are you using, and are the ESP32 and motor sharing it?
* What motor driver, transistor, or relay are you using to control the motor?
* Does the serial monitor display an error message right as the board restarts?

### 4. Safety notes
Never connect a DC motor directly to an ESP32 GPIO pin. Motors draw far more current than a GPIO pin can deliver and produce high-voltage spikes, which can permanently destroy the ESP32. Always use a dedicated driver or transistor circuit.
