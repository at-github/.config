#!/usr/bin/env python3
"""Print the weather from OpenWeatherMap as JSON (for defpoll).

Weather Icons glyphs, day and night variants; the wind with its Beaufort
force.
The bar closes on every fullscreen and defpoll restarts the script when it
reopens: the cache avoids calling the weather API every time.
"""
import json
import time
from pathlib import Path

import requests

CITY = "Parly"
COUNTRY = "FR"
URL = "https://api.openweathermap.org/data/2.5/weather"
KEY_FILE = Path.home() / ".owm-key"
CACHE_SECONDS = 3600
CACHE = Path.home() / ".cache/eww/weather.json"
FIELDS = ("icon", "temp", "wind_icon", "wind", "tooltip")

# (highest weather id, day icon, night icon), see openweathermap.org/weather-conditions
CONDITION_ICONS = (
    (232, "\ue30f", "\ue32a"),  # Thunderstorm
    (321, "\ue306", "\ue326"),  # Drizzle
    (531, "\ue308", "\ue325"),  # Rain
    (622, "\uf2dc", "\uf2dc"),  # Snow
    (771, "\ue313", "\ue313"),  # Fog
    # The other ids up to 804 show as overcast
    (780, "\ue312", "\ue312"),
    (781, "\ue351", "\ue351"),  # Tornado
    (799, "\ue312", "\ue312"),
    (800, "\ue30d", "\uf186"),  # Clear sky
    (801, "\ue376", "\ue377"),  # Few clouds
    (804, "\ue312", "\ue312"),  # Overcast
)
UNKNOWN_ICON = "\uf128"

# (highest speed in km/h, Beaufort icon), from force 0 to 11; force 12 above
BEAUFORT_ICONS = (
    (1, "\ue3af"),
    (5, "\ue3b0"),
    (11, "\ue3b1"),
    (19, "\ue3b2"),
    (28, "\ue3b3"),
    (38, "\ue3b4"),
    (49, "\ue3b5"),
    (61, "\ue3b6"),
    (74, "\ue3b7"),
    (88, "\ue3b8"),
    (102, "\ue3b9"),
    (117, "\ue3ba"),
)
HURRICANE_ICON = "\ue3bb"


def condition_icon(weather_id, is_day):
    for highest_id, day_icon, night_icon in CONDITION_ICONS:
        if weather_id <= highest_id:
            return day_icon if is_day else night_icon
    return UNKNOWN_ICON


def beaufort_icon(speed):
    return next((icon for highest, icon in BEAUFORT_ICONS if speed <= highest), HURRICANE_ICON)


def fetch():
    response = requests.get(
        URL,
        params={
            "q": f"{CITY},{COUNTRY}",
            "appid": KEY_FILE.read_text().strip(),
            "units": "metric",
            "lang": "fr",
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    now = time.time()
    is_day = data["sys"]["sunrise"] <= now <= data["sys"]["sunset"]
    # m/s to km/h, decimals cut
    wind = int(data["wind"]["speed"] * 3.6)
    return {
        "icon": condition_icon(data["weather"][0]["id"], is_day),
        "temp": f"{round(data['main']['temp'])}°",
        "wind_icon": beaufort_icon(wind),
        "wind": str(wind),
        "tooltip": f"Météo à {CITY} : {data['weather'][0]['description']}",
    }


def read_cache():
    """Cached weather, if it has all the fields (older caches lack some)."""
    try:
        weather = json.loads(CACHE.read_text())
    except (OSError, ValueError):
        return None
    return weather if all(field in weather for field in FIELDS) else None


def main():
    cached = read_cache()
    if cached and time.time() - CACHE.stat().st_mtime < CACHE_SECONDS:
        print(json.dumps(cached, ensure_ascii=False))
        return
    try:
        weather = fetch()
    except (OSError, requests.RequestException, ValueError, KeyError, IndexError):
        weather = None
    if weather is None:
        fallback = {"icon": "", "temp": "?", "wind_icon": "", "wind": "", "tooltip": "Météo indisponible"}
        print(json.dumps(cached or fallback, ensure_ascii=False))
        return
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(weather, ensure_ascii=False))
    print(json.dumps(weather, ensure_ascii=False))


main()
