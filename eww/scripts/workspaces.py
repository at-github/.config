#!/usr/bin/env python3
"""Print the i3 workspaces as JSON, now and on each change (for deflisten)."""
import json

import i3ipc

# Icon of each workspace, by name; the others show their name
ICONS = {
    "1": "\U000f0644",
    "2": "\U000f0c11",
    "3": "\uf07c",
    "4": "\U000f0474",
    "5": "\U000f0d13",
    "6": "\U000f0a08",
    "7": "\uf444",
    "8": "\uf444",
    "9": "\uf444",
    "10": "\U000f0386",
}


def print_workspaces(i3, _=None):
    workspaces = [
        {
            "num": ws.num,
            "icon": ICONS.get(ws.name, ws.name),
            "focused": ws.focused,
            "urgent": ws.urgent,
        }
        for ws in i3.get_workspaces()
    ]
    print(json.dumps(workspaces, ensure_ascii=False), flush=True)


i3 = i3ipc.Connection(auto_reconnect=True)
i3.on(i3ipc.Event.WORKSPACE, print_workspaces)
print_workspaces(i3)
i3.main()
