#!/usr/bin/env python3
"""Print the bar's Home Assistant blocks as JSON (for defpoll).

A line that cannot be read shows a red bug icon, the reason in its tooltip.
"""
import json

from ha_errors import BIN, BUG_ICON, Unreadable, entity, fetch_states, number

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


def line_value(entity_ids, states):
    """Sum of the entities; Unreadable names the first one that fails."""
    # Home Assistant itself failed: same reason on every line
    if isinstance(states, Unreadable):
        raise states
    return sum(
        number(entity(states, entity_id)["state"], entity_id, "la valeur")
        for entity_id in entity_ids
    )


def is_alert(name, value):
    if name not in ALERT_BOUNDS:
        return False
    low, high = ALERT_BOUNDS[name]
    # Compare the displayed (rounded) value, so "45°" is never shown in red
    return not low <= round(value) <= high


def build_line(name, reference, entities, states):
    names = [reference] if isinstance(reference, str) else reference
    entity_ids = [entities[entity]["entity_id"] for entity in names]
    line = {"name": name, "icon": ICONS.get(name, "")}
    try:
        value = line_value(entity_ids, states)
    except Unreadable as error:
        return line | {"text": BUG_ICON, "alert": True, "tooltip": f"{TOOLTIPS[name]} : {error}"}
    return line | {
        "text": FORMATS[name](value),
        "alert": is_alert(name, value),
        "tooltip": TOOLTIPS[name],
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
    try:
        states = fetch_states()
    except Unreadable as error:
        states = error
    blocks = [
        build_block(display, document["entities"], states)
        for display in document["displays"]["eww"]
    ]
    # Untitled blocks (solar) last, below the rooms
    blocks.sort(key=lambda block: block["label"] == "")
    print(json.dumps(blocks, ensure_ascii=False))


main()
