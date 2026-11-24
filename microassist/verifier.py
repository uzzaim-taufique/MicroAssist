"""Verification check for AI recommendations (SCRUM-17).

The AI can "hallucinate": name a chip that does not exist or give a wrong
clock speed or memory size. After the recommendation agent answers, this
module reads the answer and checks it against the verified database:

1. Every microcontroller or board name found in the answer is looked up.
   Names that are in the database are "verified"; the rest are "unverified".
2. Every clock speed (MHz) and memory size (KB/MB) in the answer is compared
   with the database values of the verified parts. Values that do not match
   are "unverified".

The check is deliberately cautious: anything it cannot confirm is reported
as unverified, with advice to check the official datasheet.
"""

import re

from microassist.database import find_part, load_database

# Chip part numbers, e.g. ESP32-S3, STM32F103C8T6, RP2040, nRF52840, ATmega328P.
CHIP_PATTERN = re.compile(
    r"\b(?:ATmega|ATtiny|ATSAMD|SAMD|ESP|STM32|GD32|CH32|RP|nRF|PIC|MSP430|i\.?MX ?RT|iMXRT|MIMXRT|RA\d|R7FA|CYW)"
    r"[A-Za-z0-9]*"
    r"(?:-(?:S2|S3|C2|C3|C5|C6|H2|P4|WROOM|WROVER|MINI|DevKitC|DevKitM|DevKit|PU|AU|[0-9]+[A-Za-z]*|[A-Z][0-9]+[A-Za-z]*))*",
    re.IGNORECASE)
# Development boards, e.g. Arduino Uno R4 WiFi, Raspberry Pi Pico W, Teensy 4.1.
BOARD_PATTERN = re.compile(
    r"\bArduino (?:Uno|Nano|Mega|Leonardo|Micro|Zero|Due|MKR \w+|Pro Mini|Portenta \w+|GIGA)"
    r"(?: (?:R3|R4|Rev3|2560|Every|33 BLE Sense|33 BLE|33 IoT|ESP32|RP2040 Connect|WiFi|Minima))*"
    r"|\bRaspberry Pi Pico(?: 2)?(?: W)?|\bTeensy ?\d(?:\.\d)?|\bNodeMCU(?:-32S)?|\bBlue Pill|\bBlack Pill",
    re.IGNORECASE)
# Family names on their own ("the STM32 family") are not specific parts.
GENERIC_NAMES = {"esp", "stm32", "pic", "avr", "nrf52", "samd", "rp", "msp430", "gd32", "ch32", "atmega", "attiny"}

SPEC_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(MHz|KB|kB|KiB|MB|MiB)\b")
DATASHEET_ADVICE = "check the official datasheet before relying on it"


def _part_names(text):
    """Find chip and board names in the text, in order, without duplicates.

    Board names are found first and their text is "used up", so the ESP32 in
    "Arduino Nano ESP32" is not counted again as a separate ESP32 chip.
    """
    found, taken = [], []
    for pattern in (BOARD_PATTERN, CHIP_PATTERN):
        for match in pattern.finditer(text):
            if any(match.start() < end and match.end() > start for start, end in taken):
                continue
            name = match.group(0).strip()
            if pattern is CHIP_PATTERN and not any(ch.isdigit() for ch in name):
                continue  # "ESP" or "PIC" alone is not a part number
            if name.lower() in GENERIC_NAMES:
                continue
            taken.append(match.span())
            if name.lower() not in [f.lower() for f in found]:
                found.append(name)
    return found


def _allowed_values(entries):
    mhz, kb = set(), set()
    for e in entries:
        mhz.update(float(v) for v in e["clock_mhz"])
        for field in ("flash_kb", "ram_kb", "eeprom_kb"):
            if e.get(field):
                kb.add(float(e[field]))
    return mhz, kb


def verify(answer, database=None):
    """Check an AI answer against the database.

    Returns a dict with:
      verified:          list of (name in answer, database name)
      unverified_parts:  part names not found in the database
      unverified_specs:  clock/memory values that do not match the verified parts
    """
    database = database if database is not None else load_database()
    verified, unverified_parts, entries = [], [], []
    for name in _part_names(answer or ""):
        entry = find_part(name, database)
        if entry:
            verified.append((name, entry["name"]))
            if entry not in entries:
                entries.append(entry)
        elif not any(name.lower() in v[0].lower() for v in verified):
            unverified_parts.append(name)

    mhz_ok, kb_ok = _allowed_values(entries)
    unverified_specs = []
    for number, unit in SPEC_PATTERN.findall(answer or ""):
        value = float(number)
        if unit == "MHz":
            ok = value in mhz_ok
        else:
            kb = value * 1024 if unit.upper().startswith("M") else value
            ok = kb in kb_ok
        label = f"{number} {unit}"
        if not ok and label not in unverified_specs:
            unverified_specs.append(label)

    return {"verified": verified, "unverified_parts": unverified_parts, "unverified_specs": unverified_specs}


def format_report(result):
    """Turn the result of verify() into text to print under the answer."""
    lines = ["--- Verification (checked against the MicroAssist database) ---"]
    if result["verified"]:
        names = ", ".join(sorted({db_name for _, db_name in result["verified"]}))
        lines.append(f"Verified in database: {names}")
    else:
        lines.append("No microcontroller from the database was found in this answer.")
    for name in result["unverified_parts"]:
        lines.append(f"UNVERIFIED part: {name} is not in the database - {DATASHEET_ADVICE}.")
    for spec in result["unverified_specs"]:
        lines.append(f"UNVERIFIED specification: {spec} does not match the database - {DATASHEET_ADVICE}.")
    if not result["unverified_parts"] and not result["unverified_specs"] and result["verified"]:
        lines.append("All named parts and clock/memory values match the database.")
    return "\n".join(lines)
