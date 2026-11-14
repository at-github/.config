#!/usr/bin/env python3
"""Print the bar's weather cells from Home Assistant as JSON (for defpoll).

Two cells: the sky (Météo-France sky icon, day and night variants, with the
outdoor probe and the forecast temperatures on one line, "5/6°", the probe in
bold) and the wind
with its Beaufort force. A value that cannot be read shows a red bug icon, the
reason in its tooltip.
"""
import json

from ha_errors import BUG_ICON, Unreadable, entity, fetch_states, number

FORECAST = "weather.meteo_france_forecast_for_city_parly_bourgogne_89_fr_parly"
PROBE = "sensor.capteur_thermique_exterieur_sud_temperature"
SUN = "sun.sun"

# Longer texts ("-12/-10°") overflow the bar width: shown smaller
SMALL_TEXT_FROM = 7

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
    return {"icon": icon, "text": text, "tooltip": tooltip, "alert": False, "small": False, "markup": ""}


def bug_cell(what, reason):
    return {"icon": BUG_ICON, "text": "", "tooltip": f"{what} : {reason}", "alert": True, "small": False, "markup": ""}


def beaufort_icon(speed):
    return next((icon for highest, icon in BEAUFORT_ICONS if speed <= highest), HURRICANE_ICON)


def probe_reading(states):
    """Measured temperature and its tooltip line; the bug icon when unreadable."""
    try:
        temperature = number(entity(states, PROBE)["state"], PROBE, "la valeur")
    except Unreadable as error:
        return BUG_ICON, f"Sonde : {error}"
    measured = f"{temperature:.1f}".replace(".", ",")
    return str(round(temperature)), f"Sonde : {measured}°"


def sky_cell(states):
    forecast = entity(states, FORECAST)
    temperature = number(forecast["attributes"].get("temperature"), FORECAST, "la température")
    # Unknown sun: day icons
    is_night = states.get(SUN, {}).get("state") == "below_horizon"
    day_icon, night_icon, description = CONDITIONS.get(
        forecast["state"], (UNKNOWN_ICON, UNKNOWN_ICON, forecast["state"])
    )
    probe, probe_tooltip = probe_reading(states)
    # Measured (bold) / forecast; one degree sign to fit the bar width
    forecast_text = f"{round(temperature)}°"
    text = f"{probe}/{forecast_text}"
    return cell(
        night_icon if is_night else day_icon,
        text,
        f"{description[:1].upper()}{description[1:]}\n{probe_tooltip} / Prévision : {forecast_text}",
    ) | {
        "markup": f"<b>{probe}</b>/{forecast_text}",
        "alert": probe == BUG_ICON,
        "small": len(text) >= SMALL_TEXT_FROM,
    }


def wind_cell(states):
    forecast = entity(states, FORECAST)
    # Decimals cut, in the unit set in Home Assistant
    speed = int(number(forecast["attributes"].get("wind_speed"), FORECAST, "la vitesse du vent"))
    unit = forecast["attributes"].get("wind_speed_unit", "km/h")
    return cell(beaufort_icon(speed), str(speed), f"Vent (Météo-France) : {speed} {unit}")


# Key in the JSON: (name in the error tooltips, builder)
CELLS = {
    "sky": ("Météo", sky_cell),
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
