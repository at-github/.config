#!/usr/bin/env -S python3 -I -S
"""Minimal Kodi control through its local JSON-RPC TCP interface (port 9090).

Kodi does not expose MPRIS, so playerctl cannot see it. osd.sh uses this
script instead whenever Kodi has an active player.

Usage:
  kodi.py status                       print "Status<US>title<US>subtitle<US>cover"
  kodi.py play-pause|next|previous     control the active player

<US> is the unit separator (\\x1f): unlike a tab, the shell keeps the empty
fields when it splits on it. cover is a local image file, or empty.

Exits with status 1 when Kodi is not running or nothing is playing.
"""
import json
import os
import socket
import sys
import urllib.parse

HOST, PORT = "127.0.0.1", 9090
TIMEOUT = 0.5
SEPARATOR = "\x1f"
# Kodi's image cache (special://thumbnails)
THUMBNAILS = os.path.expanduser("~/.kodi/userdata/Thumbnails")
# Cover of the item, by preference: posters (movies, shows), then album covers
ART_KEYS = ("poster", "tvshow.poster", "thumb", "album.thumb")


def rpc(method, params=None):
    with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as sock:
        request = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        sock.sendall(json.dumps(request).encode())
        buffer = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                raise ConnectionError("Kodi closed the connection")
            buffer += chunk
            try:
                return json.loads(buffer).get("result")
            except ValueError:
                continue  # response not complete yet


def active_player():
    players = rpc("Player.GetActivePlayers") or []
    if not players:
        sys.exit(1)
    return players[0]["playerid"]


def cover(item):
    """Local file of the item's cover: Kodi's cached copy, else the original
    when it is a local file; empty when there is none."""
    art = item.get("art") or {}
    url = next((art[key] for key in ART_KEYS if art.get(key)), item.get("thumbnail", ""))
    if not url:
        return ""
    # image://<percent-encoded original>/
    original = url
    if url.startswith("image://"):
        original = urllib.parse.unquote(url[len("image://"):].rstrip("/"))
    for candidate in (original, url):
        textures = rpc("Textures.GetTextures", {
            "filter": {"field": "url", "operator": "is", "value": candidate},
            "properties": ["cachedurl"],
        }) or {}
        for texture in textures.get("textures") or []:
            path = os.path.join(THUMBNAILS, texture["cachedurl"])
            if os.path.isfile(path):
                return path
    return original if os.path.isfile(original) else ""


def status(player):
    speed = rpc("Player.GetProperties", {"playerid": player, "properties": ["speed"]})["speed"]
    item = rpc("Player.GetItem", {
        "playerid": player,
        "properties": ["title", "artist", "showtitle", "season", "episode", "art", "thumbnail"],
    })["item"]

    title = item.get("title") or item.get("label", "")
    if item.get("type") == "episode" and item.get("showtitle"):
        subtitle = item["showtitle"]
        if item.get("season", -1) >= 0 and item.get("episode", -1) >= 0:
            subtitle += f" S{item['season']:02d}E{item['episode']:02d}"
    else:
        subtitle = ", ".join(item.get("artist") or [])

    fields = ("Playing" if speed else "Paused", title, subtitle, cover(item))
    print(SEPARATOR.join(fields))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    command = sys.argv[1]
    try:
        player = active_player()
        if command == "status":
            status(player)
        elif command == "play-pause":
            rpc("Player.PlayPause", {"playerid": player})
        elif command in ("next", "previous"):
            rpc("Player.GoTo", {"playerid": player, "to": command})
        else:
            sys.exit(__doc__)
    except (OSError, ConnectionError, KeyError, TypeError):
        sys.exit(1)


if __name__ == "__main__":
    main()
