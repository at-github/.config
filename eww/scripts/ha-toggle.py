#!/usr/bin/env python3
"""Toggle a Home Assistant switch from the bar, then refresh the bar.

Usage: ha-toggle.py <switch entity id>

The bar is refreshed as soon as Home Assistant reports the new state, then
once more a few seconds later, when the plug has measured its new power.
A failure shows up as a notification.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from ha_errors import BIN, request_error

from home_assistant import HomeAssistant  # noqa: E402  (BIN is on sys.path)

SCRIPTS = Path(__file__).parent
STATE_WAIT = 5  # seconds to wait for the new switch state
POWER_DELAY = 5  # seconds before the second refresh


def refresh_bar():
    blocks = subprocess.run(
        [SCRIPTS / "home-assistant.py"], capture_output=True, text=True, check=True
    ).stdout
    subprocess.run(["eww", "update", f"home_assistant={blocks}"], check=True)


def main():
    entity_id = sys.argv[1]
    load_dotenv(BIN / ".env")
    url = os.environ["HA_URL"]
    home_assistant = HomeAssistant(url=url, token=os.environ["HA_TOKEN"])
    try:
        before = home_assistant.states()[entity_id]["state"]
        home_assistant.call_service("switch", "toggle", entity_id)
        deadline = time.monotonic() + STATE_WAIT
        while time.monotonic() < deadline:
            time.sleep(0.5)
            if home_assistant.states()[entity_id]["state"] != before:
                break
    except requests.RequestException as error:
        subprocess.run([
            "notify-send", "-u", "critical", "Bascule impossible",
            f"{entity_id} : Home Assistant ({url}) {request_error(error)}",
        ])
        return
    refresh_bar()
    time.sleep(POWER_DELAY)
    refresh_bar()


main()
