"""Read Home Assistant states for the bar, with plain-words reasons on failure.

Shared by home-assistant.py and weather.py: a value that cannot be read
raises Unreadable, whose message goes to the cell tooltip next to a red bug
icon.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

BIN = Path.home() / ".local/bin"
sys.path.insert(0, str(BIN))

from home_assistant import HomeAssistant  # noqa: E402

BUG_ICON = "\U000f00e4"
UNREADABLE_STATES = ("unavailable", "unknown")


class Unreadable(Exception):
    """A value the bar cannot show; the message says why."""


def request_error(error):
    """What went wrong with the Home Assistant request, in plain words."""
    if isinstance(error, requests.Timeout):
        return "ne répond pas à temps (serveur lent ou éteint ?)"
    if isinstance(error, requests.ConnectionError):
        return "est injoignable (serveur éteint ou réseau coupé ?)"
    if isinstance(error, requests.HTTPError):
        status = error.response.status_code
        hint = " : jeton HA_TOKEN refusé ?" if status in (401, 403) else ""
        return f"répond par une erreur HTTP {status}{hint}"
    return f"a échoué ({type(error).__name__})"


def fetch_states():
    """All the states by entity id; Unreadable if Home Assistant fails."""
    load_dotenv(BIN / ".env")
    url = os.environ["HA_URL"]
    try:
        return HomeAssistant(url=url, token=os.environ["HA_TOKEN"]).states()
    except requests.RequestException as error:
        raise Unreadable(f"Home Assistant ({url}) {request_error(error)}") from None


def entity(states, entity_id):
    """The state of a readable entity."""
    try:
        state = states[entity_id]
    except KeyError:
        raise Unreadable(f"l'entité {entity_id} n'existe pas dans Home Assistant") from None
    if state["state"] in UNREADABLE_STATES:
        since = datetime.fromisoformat(state["last_changed"]).astimezone().strftime("%d/%m %H:%M")
        raise Unreadable(f"{entity_id} est « {state['state']} » depuis le {since}")
    return state


def number(value, entity_id, what):
    """value as a float; `what` names it in the message ("la valeur")."""
    try:
        return float(value)
    except (TypeError, ValueError):
        raise Unreadable(f"{what} de {entity_id} n'est pas un nombre ({value!r})") from None
