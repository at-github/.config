#!/usr/bin/env python3
"""Print the network icon and download speed as JSON (for deflisten)."""
import json
import time
from pathlib import Path

INTERVAL = 5  # seconds

ICON_WIRED = "\U000f0002"
ICON_WIFI = "\U000f05a9"
ICON_OFFLINE = "\U000f0be1"


def default_interface():
    with open("/proc/net/route") as routes:
        next(routes)
        fields = [line.split() for line in routes]
    defaults = [(int(f[6]), f[0]) for f in fields if f[1] == "00000000"]
    return min(defaults)[1] if defaults else None


def human_speed(bytes_per_second):
    value = bytes_per_second / 1024
    for unit in "KMG":
        if value < 1000 or unit == "G":
            return f"{value:.1f}{unit}" if value < 10 else f"{value:.0f}{unit}"
        value /= 1024


previous_interface, previous_rx = None, 0
while True:
    icon, speed = ICON_OFFLINE, ""
    interface = default_interface()
    if interface:
        path = Path("/sys/class/net", interface)
        rx = int((path / "statistics/rx_bytes").read_text())
        icon = ICON_WIFI if (path / "wireless").exists() else ICON_WIRED
        delta = rx - previous_rx if interface == previous_interface else 0
        speed = human_speed(delta / INTERVAL)
        previous_interface, previous_rx = interface, rx
    print(json.dumps({"icon": icon, "speed": speed}, ensure_ascii=False), flush=True)
    time.sleep(INTERVAL)
