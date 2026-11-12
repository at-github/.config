#!/usr/bin/env -S python3 -I -S
"""Minimal Kodi control through its local JSON-RPC TCP interface (port 9090).

Kodi does not expose MPRIS, so playerctl cannot see it. osd.sh uses this
script instead whenever Kodi has an active player.

Usage:
  kodi.py status                       print "Status<TAB>title<TAB>subtitle"
  kodi.py play-pause|next|previous     control the active player

Exits with status 1 when Kodi is not running or nothing is playing.
"""
import json
import socket
import sys

HOST, PORT = "127.0.0.1", 9090
TIMEOUT = 0.5


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


def status(player):
    speed = rpc("Player.GetProperties", {"playerid": player, "properties": ["speed"]})["speed"]
    item = rpc("Player.GetItem", {
        "playerid": player,
        "properties": ["title", "artist", "showtitle", "season", "episode"],
    })["item"]

    title = item.get("title") or item.get("label", "")
    if item.get("type") == "episode" and item.get("showtitle"):
        subtitle = item["showtitle"]
        if item.get("season", -1) >= 0 and item.get("episode", -1) >= 0:
            subtitle += f" S{item['season']:02d}E{item['episode']:02d}"
    else:
        subtitle = ", ".join(item.get("artist") or [])

    print(f"{'Playing' if speed else 'Paused'}\t{title}\t{subtitle}")


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
