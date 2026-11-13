#!/usr/bin/env python3
"""Print the bar's weather cells from Home Assistant as JSON (for defpoll).

Three cells: the Météo-France forecast (sky icon, day and night variants),
the outdoor probe and the wind with its Beaufort force. A cell that cannot be
read shows a red bug icon, the reason in its tooltip.
"""
import json

from ha_errors import BUG_ICON, Unreadable, entity, fetch_states, number

CITY = "Parly"
FORECAST = "weather.meteo_france_forecast_for_city_parly_bourgogne_89_fr_parly"
PROBE = "sensor.capteur_thermique_exterieur_sud_temperature"
SUN = "sun.sun"

PROBE_ICON = ""

# Home Assistant condition: (day icon, night icon, French description)
CONDITIONS = {
    "clear-night": ("", "", "ciel dégagé"),
    "sunny": ("", "", "ensoleillé"),
    "partlycloudy": ("", "", "partiellement nuageux"),
    "cloudy": ("", "", "nuageux"),
    "fog": ("", "", "brouillard"),
    "rainy": ("", "", "pluie"),
    "pouring": ("", "", "averses"),
    "lightning": ("", "", "orage"),
    "lightning-rainy": ("", "", "orage et pluie"),
    "snowy": ("", "", "neige"),
    "snowy-rainy": ("", "", "pluie et neige"),
    "hail": ("", "", "grêle"),
    "windy": ("", "", "venteux"),
    "windy-variant": ("", "", "venteux et nuageux"),
    "exceptional": ("", "", "conditions exceptionnelles"),
}
UNKNOWN_ICON = ""

# (highest speed in km/h, Beaufort icon), from force 0 to 11; force 12 above
BEAUFORT_ICONS = (
    (1, ""),
    (5, ""),
    (11, ""),
    (19, ""),
    (28, ""),
    (38, ""),
    (49, ""),
    (61, ""),
    (74, ""),
    (88, ""),
    (102, ""),
    (117, ""),
)
HURRICANE_ICON = ""


def cell(icon, text, tooltip):
    return {"icon": icon, "text": text, "tooltip": tooltip, "alert": False}


def bug_cell(what, reason):
    return {"icon": BUG_ICON, "text": "", "tooltip": f"{what} : {reason}", "alert": True}


def beaufort_icon(speed):
    return next((icon for highest, icon in BEAUFORT_ICONS if speed <= highest), HURRICANE_ICON)


def sky_cell(states):
    forecast = entity(states, FORECAST)
    temperature = number(forecast["attributes"].get("temperature"), FORECAST, "la température")
    # Unknown sun: day icons
    is_night = states.get(SUN, {}).get("state") == "below_horizon"
    day_icon, night_icon, description = CONDITIONS.get(
        forecast["state"], (UNKNOWN_ICON, UNKNOWN_ICON, forecast["state"])
    )
    return cell(
        night_icon if is_night else day_icon,
        f"{round(temperature)}°",
        f"Prévision Météo-France à {CITY} : {description}",
    )


def probe_cell(states):
    probe = entity(states, PROBE)
    temperature = number(probe["state"], PROBE, "la valeur")
    return cell(PROBE_ICON, f"{round(temperature)}°", "Température mesurée par la sonde extérieure (sud)")


def wind_cell(states):
    forecast = entity(states, FORECAST)
    # Decimals cut, in the unit set in Home Assistant
    speed = int(number(forecast["attributes"].get("wind_speed"), FORECAST, "la vitesse du vent"))
    unit = forecast["attributes"].get("wind_speed_unit", "km/h")
    return cell(beaufort_icon(speed), str(speed), f"Vent (Météo-France) : {speed} {unit}")


# Key in the JSON: (name in the error tooltips, builder)
CELLS = {
    "sky": ("Météo", sky_cell),
    "probe": ("Sonde extérieure", probe_cell),
    "wind": ("Vent", wind_cell),
}


def main():
    try:
        states = fetch_states()
    except Unreadable as error:
        print(json.dumps({key: bug_cell(what, error) for key, (what, _) in CELLS.items()}, ensure_ascii=False))
        return
    weather = {}
    for key, (what, build) in CELLS.items():
        try:
            weather[key] = build(states)
        except Unreadable as error:
            weather[key] = bug_cell(what, error)
    print(json.dumps(weather, ensure_ascii=False))


main()
