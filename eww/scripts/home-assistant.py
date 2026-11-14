#!/usr/bin/env python3
"""Print the bar's Home Assistant blocks as JSON (for defpoll).

A line that cannot be read shows a red bug icon, the reason in its tooltip.
"""
import json
from datetime import datetime

from ha_errors import BIN, BUG_ICON, Unreadable, entity, fetch_states, number

FORMATS = {
    "temperature": lambda value: f"{value:.0f}°",
    "humidity": lambda value: f"{value:.0f}%",
    "battery_level": lambda value: f"{value:.0f}%",
    "output_power": lambda value: f"{value:.0f}W",
    "solar_power": lambda value: f"{value:.0f}W",
    "ac_input_power": lambda value: f"{value:.0f}W",
    "cell_temperature": lambda value: f"{value:.0f}°",
    "plug": lambda value: f"{value:.0f}W",
}
TOOLTIPS = {
    "temperature": "Température",
    "humidity": "Humidité",
    "battery_level": "Charge de la batterie",
    "output_power": "Puissance de sortie totale",
    "solar_power": "Puissance d'entrée solaire",
    "ac_input_power": "Puissance d'entrée secteur",
    "cell_temperature": "Température des cellules — rouge sous 5° ou au-dessus de 45°",
    "plug": "clic pour basculer",
}
# (low, high) bounds outside of which a value is worrying.
# Cell temperature: charging resumes above 5°C, 45°C is the manual's upper limit.
ALERT_BOUNDS = {
    "cell_temperature": (5, 45),
}
# Battery thresholds, read from the EcoFlow settings: red at or below the
# backup reserve (the discharge limit when the reserve is off) plus a margin,
# inverted colors from the charge limit up (maintenance charges reach 100%)
BATTERY_LOW_MARGIN = 5
BATTERY_SETTINGS = {
    "discharge_limit": "delta2max_charge_limit_min",
    "charge_limit": "delta2max_charge_limit_max",
    "reserve": "delta2max_backup_reserve",
    "reserve_enabled": "delta2max_backup_reserve_enabled",
}
# Lines highlighted (inverted colors) while their displayed value is not 0
HIGHLIGHT_NONZERO = {"output_power", "solar_power", "ac_input_power"}
# Line icons; the AC input one mirrors the output one
ICONS = {
    "battery_level": "\U000f0080",
    "cell_temperature": "\U000f050f",
    "output_power": "",
    "solar_power": "",
    "ac_input_power": "",
    "plug": "\U000f1108",
    "window": "\U000f11dc",
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


def is_active(name, value):
    # Compare the displayed (rounded) value, so "0W" is never highlighted
    return name in HIGHLIGHT_NONZERO and round(value) != 0


def battery_thresholds(entities, states):
    """(low, high) battery levels; Unreadable names the setting that fails."""
    def state(setting):
        entity_id = entities[BATTERY_SETTINGS[setting]]["entity_id"]
        return entity_id, entity(states, entity_id)["state"]

    def value(setting):
        entity_id, raw = state(setting)
        return number(raw, entity_id, "la valeur")

    reserve_on = state("reserve_enabled")[1] == "on"
    low = value("reserve" if reserve_on else "discharge_limit") + BATTERY_LOW_MARGIN
    return low, value("charge_limit")


def battery_colors(value, entities, states):
    """attention, active and tooltip of the battery line."""
    try:
        low, high = battery_thresholds(entities, states)
    except Unreadable as error:
        return False, False, f"{TOOLTIPS['battery_level']} (seuils illisibles : {error})"
    shown = round(value)
    tooltip = (
        f"{TOOLTIPS['battery_level']} — rouge à {low:.0f}% ou moins, "
        f"couleurs inversées dès {high:.0f}%"
    )
    return shown <= low, shown >= high, tooltip


def build_plug_line(reference, entities, states):
    """Power of a plug, highlighted while switched on; a click toggles it."""
    power_id = entities[reference["power"]]["entity_id"]
    switch_id = entities[reference["switch"]]["entity_id"]
    line = {"name": "plug", "icon": ICONS["plug"], "toggle": switch_id, "attention": False}
    try:
        power = line_value([power_id], states)
        switch = entity(states, switch_id)
    except Unreadable as error:
        return line | {
            "text": BUG_ICON,
            "alert": True,
            "active": False,
            "tooltip": f"Prise ({TOOLTIPS['plug']}) : {error}",
        }
    return line | {
        "text": FORMATS["plug"](power),
        "alert": False,
        "active": switch["state"] == "on",
        "tooltip": f"{switch['attributes'].get('friendly_name', switch_id)} — {TOOLTIPS['plug']}",
    }


def opened_since(last_changed):
    """"14:32" today, "13/11 14:32" before."""
    moment = datetime.fromisoformat(last_changed).astimezone()
    if moment.date() == datetime.now().date():
        return moment.strftime("%H:%M")
    return moment.strftime("%d/%m %H:%M")


def build_window_line(reference, entities, states, display_name):
    """Open window icon, highlighted; None while closed (nothing shown)."""
    entity_id = entities[reference]["entity_id"]
    line = {"name": "window", "icon": ICONS["window"], "toggle": "", "alert": False,
            "attention": False}
    try:
        if isinstance(states, Unreadable):
            raise states
        state = entity(states, entity_id)
    except Unreadable as error:
        return line | {"text": BUG_ICON, "alert": True, "active": False,
                       "tooltip": f"{display_name} : {error}"}
    if state["state"] != "on":
        return None
    return line | {
        "text": "",
        "active": True,
        "tooltip": f"{display_name} ouvert depuis {opened_since(state['last_changed'])}",
    }


def build_line(name, reference, entities, states, display_name):
    if name == "plug":
        return build_plug_line(reference, entities, states)
    if name == "window":
        return build_window_line(reference, entities, states, display_name)
    names = [reference] if isinstance(reference, str) else reference
    entity_ids = [entities[entity]["entity_id"] for entity in names]
    # `alert`: unreadable value (red bug icon); `attention`: worrying value
    # (whole cell like an urgent workspace)
    line = {"name": name, "icon": ICONS.get(name, ""), "toggle": "", "attention": False}
    try:
        value = line_value(entity_ids, states)
    except Unreadable as error:
        return line | {
            "text": BUG_ICON,
            "alert": True,
            "active": False,
            "tooltip": f"{TOOLTIPS[name]} : {error}",
        }
    if name == "battery_level":
        attention, active, tooltip = battery_colors(value, entities, states)
    else:
        attention, active, tooltip = is_alert(name, value), is_active(name, value), TOOLTIPS[name]
    return line | {
        "text": FORMATS[name](value),
        "alert": False,
        "attention": attention,
        "active": active,
        "tooltip": tooltip,
    }


def build_block(display, entities, states):
    lines = [
        build_line(name, reference, entities, states, display.get("name", ""))
        for name, reference in display.items()
        if name not in ("label", "name")
    ]
    lines = [line for line in lines if line is not None]
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
    # Blocks with nothing to show (closed window) are hidden
    blocks = [block for block in blocks if block["lines"]]
    # Untitled blocks (solar, velux) last, below the rooms
    blocks.sort(key=lambda block: block["label"] == "")
    print(json.dumps(blocks, ensure_ascii=False))


main()
