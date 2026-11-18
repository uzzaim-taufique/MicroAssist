# Debugger test 2 (SCRUM-23)

- Run: 2026-11-18 10:34 via microassist/debugger.py get_debug_help()
- Model: gemini-3.8-flash
- Prompt: prompts/debugger_v1.md

## Input

Arduino IDE shows: `avrdude: stk500_recv(): programmer is not responding`

## Response

### 1. Problem summary
The Arduino IDE cannot communicate with your board during sketch upload, resulting in the `avrdude: stk500_recv(): programmer is not responding` timeout error.

---

### 2. Likely causes and fixes

* **Wrong COM Port or Board selected**
  * **Why:** The computer is sending the upload commands to the wrong serial port or expecting a different microcontroller model.
  * **Check:** In Arduino IDE, check what is ticked under **Tools > Port** and **Tools > Board**.
  * **Fix:** Select the correct board model and the port assigned to your board. If using an Arduino Nano clone, also try changing **Tools > Processor** to "ATmega328P (Old Bootloader)".

* **Components connected to digital pins 0 (RX) and 1 (TX)**
  * **Why:** Pins 0 and 1 share the serial line used by the USB chip to flash the microcontroller. External modules disrupt this signal.
  * **Check:** Look at pins 0 and 1 to see if any wires, sensors, or shields are attached.
  * **Fix:** Unplug all connections from pins 0 and 1, upload your sketch, and reconnect them afterward.

* **Charge-only USB cable or missing USB drivers**
  * **Why:** Some micro-USB cables only supply power and lack data lines, or the PC lacks drivers for CH340/CP2102 chips.
  * **Check:** Unplug and replug the board. Check if the Port list changes or if your operating system makes a connection sound.
  * **Fix:** Use a verified data-transfer USB cable, or install the driver required by your board's USB-to-serial chip.

---

### 3. Information needed
1. Which exact Arduino board model are you using (e.g., Uno R3, Nano, Mega 2560)?
2. Do you have any wires or shields connected to pins 0 and 1?
3. Does a port appear under **Tools > Port** when you plug the board in?

---

### 4. Safety notes
Disconnect the USB cable before adding or removing wiring to prevent accidental short circuits.
