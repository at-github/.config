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
    "cell_temperature": lambda value: f"{value:.0f}°",
}
TOOLTIPS = {
    "temperature": "Température",
    "humidity": "Humidité",
    "battery_level": "Charge de la batterie",
    "output_power": "Puissance de sortie totale",
    "solar_power": "Puissance d'entrée solaire",
    "ac_input_power": "Puissance d'entrée secteur",
    "cell_temperature": "Température des cellules — rouge sous 5° ou au-dessus de 45°",
}
UNAVAILABLE_TOOLTIP = "Home Assistant ne répond pas ou la valeur est indisponible"
# (low, high) bounds outside of which a value is worrying.
# Cell temperature: charging resumes above 5°C, 45°C is the manual's upper limit.
ALERT_BOUNDS = {
    "cell_temperature": (5, 45),
}
# Line icons; the AC input one mirrors the output one
ICONS = {
    "battery_level": "\U000f0080",
    "cell_temperature": "\U000f050f",
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


def line_value(entity_ids, states):
    try:
        return sum(float(states[entity_id]["state"]) for entity_id in entity_ids)
    except (KeyError, ValueError):
        return None


def is_alert(name, value):
    if value is None or name not in ALERT_BOUNDS:
        return False
    low, high = ALERT_BOUNDS[name]
    # Compare the displayed (rounded) value, so "45°" is never shown in red
    return not low <= round(value) <= high


def build_line(name, reference, entities, states):
    names = [reference] if isinstance(reference, str) else reference
    entity_ids = [entities[entity]["entity_id"] for entity in names]
    value = line_value(entity_ids, states)
    return {
        "name": name,
        "icon": ICONS.get(name, ""),
        "text": UNAVAILABLE if value is None else FORMATS[name](value),
        "alert": is_alert(name, value),
        "tooltip": UNAVAILABLE_TOOLTIP if value is None else TOOLTIPS[name],
    }


def build_block(display, entities, states):
    lines = [
        build_line(name, reference, entities, states)
        for name, reference in display.items()
        if name not in ("label", "name")
    ]
    return {
        "label": display.get("label", ""),
        "name": display.get("name", ""),
        "lines": lines,
    }


def main():
    document = json.loads((BIN / "ha_entities.json").read_text())
    states = fetch_states()
    blocks = [
        build_block(display, document["entities"], states)
        for display in document["displays"]["eww"]
    ]
    # Untitled blocks (solar) last, below the rooms
    blocks.sort(key=lambda block: block["label"] == "")
    print(json.dumps(blocks, ensure_ascii=False))


main()
