#!/usr/bin/env python3
"""Affiche en JSON la météo (pour defpoll), à partir du plugin polybar.

La barre est fermée à chaque plein écran et defpoll relance le script à la
réouverture : le cache évite d'appeler l'API météo à chaque fois.
"""
import json
import re
import subprocess
import time
from pathlib import Path

CITY = "Parly"
CACHE_SECONDS = 3600
PLUGIN = Path.home() / ".config/polybar/modules/weather-polybar-plugin/weather-plugin.sh"
CACHE = Path.home() / ".cache/eww/weather.json"


def fetch():
    """Extrait icône, température et vent de la sortie formatée pour polybar."""
    output = subprocess.run(
        [PLUGIN, CITY], capture_output=True, text=True, timeout=30
    ).stdout
    icons = re.findall(r"%\{T4\}\s*(\S)", output)
    temperature = re.search(r"(-?\d+)%\{T2\}", output)
    if not icons or not temperature:
        return None
    # Le plugin n'affiche le vent qu'à partir de 11 km/h : l'icône du vent vient
    # alors en premier, et celle du temps reste la dernière
    wind = re.search(r"(\d+) km/h", output)
    return {
        "icon": icons[-1],
        "temp": f"{temperature.group(1)}°",
        "wind_icon": icons[0] if wind and len(icons) > 1 else "",
        "wind": wind.group(1) if wind else "",
    }


def read_cache():
    return CACHE.read_text() if CACHE.exists() else None


def main():
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_SECONDS:
        print(read_cache())
        return
    try:
        weather = fetch()
    except (OSError, subprocess.TimeoutExpired):
        weather = None
    if weather is None:
        print(read_cache() or json.dumps({"icon": "", "temp": "?", "wind_icon": "", "wind": ""}))
        return
    CACHE.write_text(json.dumps(weather, ensure_ascii=False))
    print(CACHE.read_text())


main()
