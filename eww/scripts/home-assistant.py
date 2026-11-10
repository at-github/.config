#!/usr/bin/env python3
"""Print the bar's Home Assistant blocks as JSON (for defpoll)."""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

BIN = Path.home() / ".local/bin"
sys.path.insert(0, str(BIN))

from home_assistant import HomeAssistant  # noqa: E402

UNAVAILABLE = "?"
FORMATS = {
    "temperature": lambda value: f"{value:.0f}°",
    "humidity": lambda value: f"{value:.0f}%",
    "battery_level": lambda value: f"{value:.0f}%",
    "output_power": lambda value: f"{value:.0f}W",
    "solar_power": lambda value: f"{value:.0f}W",
    "ac_input_power": lambda value: f"{value:.0f}W",
}
# Same icons as polybar's ecoflow module; the AC input mirrors the output
ICONS = {
    "battery_level": "\U000f0080",
    "output_power": "",
    "solar_power": "",
    "ac_input_power": "",
}


def fetch_states():
    load_dotenv(BIN / ".env")
    client = HomeAssistant(url=os.environ["HA_URL"], token=os.environ["HA_TOKEN"])
    try:
        return client.states()
    except requests.RequestException:
        return {}


def line_text(name, entity_ids, states):
    try:
        value = sum(float(states[entity_id]["state"]) for entity_id in entity_ids)
    except (KeyError, ValueError):
        return UNAVAILABLE
    return FORMATS[name](value)


def build_line(name, reference, entities, states):
    names = [reference] if isinstance(reference, str) else reference
    entity_ids = [entities[entity]["entity_id"] for entity in names]
    return {
        "name": name,
        "icon": ICONS.get(name, ""),
        "text": line_text(name, entity_ids, states),
    }


def build_block(display, entities, states):
    lines = [
        build_line(name, reference, entities, states)
        for name, reference in display.items()
        if name != "label"
    ]
    return {"label": display.get("label", ""), "lines": lines}


def main():
    document = json.loads((BIN / "ha_entities.json").read_text())
    states = fetch_states()
    blocks = [
        build_block(display, document["entities"], states)
        for display in document["displays"]["eww"]
    ]
    print(json.dumps(blocks, ensure_ascii=False))


main()
