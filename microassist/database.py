"""Verified microcontroller database and the search tool the AI can call (SCRUM-16).

`search_microcontrollers` is given to Gemini as a tool (function calling).
Gemini decides when to call it and with which filters; the SDK runs the
Python function and sends the results back to Gemini, which then writes its
recommendation from these real specifications instead of from memory.

Every search is recorded in logs/database_searches.jsonl so the team can
check which searches the AI made (acceptance criterion 4).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "microcontrollers.json"
LOG_PATH = ROOT / "logs" / "database_searches.jsonl"
MAX_RESULTS = 10

SEARCH_LOG = []  # searches made while the app is running (used by tests)


def compact(text):
    """Lower-case text with spaces, hyphens, dots and slashes removed: 'ESP32-S3' -> 'esp32s3'."""
    return "".join(ch for ch in str(text).lower() if ch.isalnum())


def load_database(path=DATA_PATH):
    """Return the list of microcontroller entries from the JSON database."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)["microcontrollers"]


def find_part(name, database=None):
    """Return the entry whose name or alias exactly matches `name`, or None."""
    key = compact(name)
    if not key:
        return None
    for entry in database if database is not None else load_database():
        if key in {compact(entry["name"]), compact(entry["id"])} | {compact(a) for a in entry["aliases"]}:
            return entry
    return None


def _record(arguments, results):
    record = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "arguments": arguments, "result_ids": [r["id"] for r in results]}
    SEARCH_LOG.append(record)
    try:
        LOG_PATH.parent.mkdir(exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass  # logging must never stop the app from answering


def search_microcontrollers(
    name: str = "",
    needs_wifi: bool = False,
    needs_bluetooth: bool = False,
    min_flash_kb: float = 0,
    min_ram_kb: float = 0,
    logic_level_v: float = 0,
    max_results: int = 5,
) -> dict:
    """Search the MicroAssist database of verified microcontrollers and boards.

    Args:
        name: Part or board name to look for, for example "ESP32", "RP2040" or
            "Arduino Uno". Leave empty to search by requirements only.
        needs_wifi: True to return only parts with built-in Wi-Fi.
        needs_bluetooth: True to return only parts with built-in Bluetooth.
        min_flash_kb: Minimum program flash in KB (0 = any).
        min_ram_kb: Minimum RAM in KB (0 = any).
        logic_level_v: Required I/O logic level, 5 or 3.3 (0 = any).
        max_results: Maximum number of parts to return (1 to 10).

    Returns:
        A dictionary with "count" and "results", a list of matching parts with
        their verified specifications.
    """
    arguments = {"name": name, "needs_wifi": needs_wifi, "needs_bluetooth": needs_bluetooth,
                 "min_flash_kb": min_flash_kb, "min_ram_kb": min_ram_kb,
                 "logic_level_v": logic_level_v, "max_results": max_results}
    key = compact(name)
    results = []
    for entry in load_database():
        names = [entry["name"], entry["id"], *entry["aliases"], *entry["example_boards"]]
        if key and not any(key in compact(n) for n in names):
            continue
        if needs_wifi and not entry["wifi"]:
            continue
        if needs_bluetooth and not entry["bluetooth"]:
            continue
        if min_flash_kb and entry["flash_kb"] < min_flash_kb:
            continue
        if min_ram_kb and entry["ram_kb"] < min_ram_kb:
            continue
        if logic_level_v and abs(entry["logic_level_v"] - logic_level_v) > 0.5:
            continue
        results.append(entry)

    limit = max(1, min(int(max_results or 5), MAX_RESULTS))
    results = results[:limit]
    _record(arguments, results)
    return {"count": len(results), "results": results}
