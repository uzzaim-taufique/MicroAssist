# Database Verification (SCRUM-30)

**File checked:** `data/microcontrollers.json`
**Checked by:** Uzzaim Taufique
**Date:** 24 Nov 2026

**How:** each value in the database was compared with the manufacturer's official datasheet or product page (links under each part).

## 1. ATmega328P
Source: [Microchip ATmega328P datasheet](https://fab.cba.mit.edu/classes/863.17/EECS/people/akaspar/project/atmega328p-datasheet.pdf) (Features, page 1), [Microchip product page](https://www.microchip.com/wwwproducts/en/atmega328p)

| Field | Database value | Datasheet value | Match? |
|---|---|---|---|
| Max clock | 20 MHz | "0 - 20MHz @ 4.5 - 5.5V" | Yes |
| Flash | 32 KB | "32KBytes of In-System Self-Programmable Flash" | Yes |
| SRAM | 2 KB | "2KBytes Internal SRAM" | Yes |
| EEPROM | 1 KB | "1KBytes EEPROM" | Yes |
| ADC | 10-bit, 8 channels (6 on Arduino Uno) | "8-channel 10-bit ADC in TQFP and QFN/MLF", "6-channel 10-bit ADC in PDIP" | Yes |

## 2. ESP32 / ESP32-WROOM-32
Source: [Espressif ESP32 Series datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf), [ESP32-WROOM-32 module datasheet](https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html)

| Field | Database value | Datasheet value | Match? |
|---|---|---|---|
| Max clock | 240 MHz | "clock frequency of up to 240 MHz" (Section 4.1.1) | Yes |
| SRAM | 520 KB | "520 KB SRAM" (Features, p. 4) | Yes |
| Flash (on WROOM-32 module) | 4 MB | "The module features a 4 MB external SPI flash" (Section 1.2) | Yes |
| Bluetooth | 4.2 Classic + BLE | "Compliant with Bluetooth v4.2 BR/EDR and Bluetooth LE" (Features, p. 3) | Yes |
| ADC | 12-bit, 18 channels | "12-bit SAR ADC up to 18 channels" (Features, p. 4) | Yes |

## 3. RP2040
Source: [Raspberry Pi RP2040 documentation](https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html), [RP2040 tech specs](https://www.raspberrypi.com/products/rp2040/specifications/)

| Field | Database value | Datasheet value | Match? |
|---|---|---|---|
| Core | Dual Cortex-M0+ | "Dual-core Arm Cortex-M0+ processor" | Yes |
| Clock | 133 MHz (200 MHz in newer datasheet) | "up to 133 MHz"; certified for 200 MHz since Pico SDK 2.1.1 (Feb 2025) | Yes (see note) |
| SRAM | 264 KB | "264kB on-chip SRAM" | Yes |
| GPIO | 30 | "30 GPIO pins, 4 of which can be used as analogue inputs" | Yes |

Note: the 200 MHz rating was announced with the Pico SDK 2.1.1 release ([Hackaday](https://hackaday.com/2025/02/20/pico-gets-a-speed-bump)), not in the datasheet pages checked, so the database note should say "since 2025 (Pico SDK 2.1.1)".

## 4. STM32F103C8
Source: [ST STM32F103C8 product page](https://www.st.com/en/microcontrollers-microprocessors/stm32f103c8.html)

| Field | Database value | Datasheet value | Match? |
|---|---|---|---|
| Max clock | 72 MHz | "72 MHz maximum frequency" | Yes |
| Flash | 64 KB | "64 Kbytes of Flash memory" | Yes |
| SRAM | 20 KB | "20 Kbytes of SRAM" | Yes |
| GPIO | 37 | 37 I/Os (orderable parts table) | Yes |

## 5. nRF52840
Source: [Nordic nRF52840 Product Specification, Key features](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/keyfeatures_html5.html)

| Field | Database value | Datasheet value | Match? |
|---|---|---|---|
| Clock | 64 MHz | "Arm Cortex-M4 32-bit processor with FPU, 64 MHz" | Yes |
| Flash | 1 MB | "1 MB flash" | Yes |
| RAM | 256 KB | "256 kB RAM" | Yes |
| Radio | Bluetooth 5 LE + 802.15.4 | "Bluetooth 5, IEEE 802.15.4-2006, 2.4 GHz transceiver" | Yes |

## Result
5 of 5 parts fully matched the official sources. One wording fix was made: the RP2040 note now says the 200 MHz rating comes from the 2025 Pico SDK 2.1.1 certification.