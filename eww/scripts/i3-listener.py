#!/usr/bin/env python3
"""Pilote la barre eww depuis les événements i3 : workspaces, position, plein écran."""
import json
import re
import subprocess
from pathlib import Path

import i3ipc

BAR_WIDTH = 40
POLYBAR_CONFIG = Path.home() / ".config/polybar/config.ini"

# Mêmes icônes que le module workspaces de polybar
ICONS = dict(re.findall(r"^icon-\d+ = (\d+);(\S+)", POLYBAR_CONFIG.read_text(), re.M))

last_geometry = None


def eww(*args):
    subprocess.run(["eww", *args], check=False)


def has_fullscreen(tree, focused):
    workspace = next(ws for ws in tree.workspaces() if ws.name == focused.name)
    return any(con.fullscreen_mode for con in workspace.descendants()) or any(
        con.fullscreen_mode == 2 for con in tree.descendants()
    )


def bar_geometry(tree, focused):
    """Colonne entre les docks i3 (polybar) du haut et du bas."""
    output = next(node for node in tree.nodes if node.name == focused.output)
    docks = {node.name: node.rect for node in output.nodes}
    top, bottom = docks["topdock"].height, docks["bottomdock"].height
    x = output.rect.x + output.rect.width - BAR_WIDTH
    return (x, output.rect.y + top, BAR_WIDTH, output.rect.height - top - bottom)


def refresh(i3, _=None):
    global last_geometry

    spaces = i3.get_workspaces()
    workspaces = json.dumps(
        [
            {
                "num": ws.num,
                "icon": ICONS.get(ws.name, ws.name),
                "focused": ws.focused,
                "urgent": ws.urgent,
            }
            for ws in spaces
        ],
        ensure_ascii=False,
    )
    eww("update", f"workspaces={workspaces}")

    # La barre échappe à i3 : c'est à nous de la retirer devant un plein écran
    tree = i3.get_tree()
    focused = next(ws for ws in spaces if ws.focused)
    geometry = None if has_fullscreen(tree, focused) else bar_geometry(tree, focused)
    if geometry == last_geometry:
        return
    if geometry is None:
        eww("close", "bar")
    else:
        x, y, width, height = geometry
        eww("open", "bar", "--pos", f"{x}x{y}", "--size", f"{width}x{height}")
    last_geometry = geometry


i3 = i3ipc.Connection(auto_reconnect=True)
for event in (
    i3ipc.Event.WORKSPACE,
    i3ipc.Event.WINDOW_FOCUS,
    i3ipc.Event.WINDOW_CLOSE,
    i3ipc.Event.WINDOW_MOVE,
    i3ipc.Event.WINDOW_FULLSCREEN_MODE,
    i3ipc.Event.OUTPUT,
):
    i3.on(event, refresh)
refresh(i3)
i3.main()
