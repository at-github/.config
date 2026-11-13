#!/usr/bin/env python3
"""Drive the eww bar from i3 events: position, fullscreen."""
import subprocess

import i3ipc

BAR_WIDTH = 60

last_geometry = None
hidden = False


def eww(*args):
    subprocess.run(["eww", *args], check=False)


def xdotool_bar(command):
    """Run an xdotool window command on the bar window (no-op if not open)."""
    subprocess.run(
        ["xdotool", "search", "--name", "^Eww - bar$", command, "%@"],
        check=False,
        stderr=subprocess.DEVNULL,
    )


def has_fullscreen(tree, focused):
    workspace = next(ws for ws in tree.workspaces() if ws.name == focused.name)
    return any(con.fullscreen_mode for con in workspace.descendants()) or any(
        con.fullscreen_mode == 2 for con in tree.descendants()
    )


def bar_geometry(tree, focused):
    """Column between the top and bottom i3 docks (other bars, if any)."""
    output = next(node for node in tree.nodes if node.name == focused.output)
    docks = {node.name: node.rect for node in output.nodes}
    top, bottom = docks["topdock"].height, docks["bottomdock"].height
    x = output.rect.x + output.rect.width - BAR_WIDTH
    return (x, output.rect.y + top, BAR_WIDTH, output.rect.height - top - bottom)


def refresh(i3, _=None):
    global last_geometry, hidden

    # The bar escapes i3 management: we must remove it in front of a fullscreen
    # window. Unmapped rather than closed: once its data is loaded, a reopened
    # bar also counts its hidden widgets and grows past the screen.
    tree = i3.get_tree()
    focused = next(ws for ws in i3.get_workspaces() if ws.focused)
    if has_fullscreen(tree, focused):
        if not hidden:
            xdotool_bar("windowunmap")
            hidden = True
        return
    geometry = bar_geometry(tree, focused)
    if geometry != last_geometry:
        # xdotool cannot move it: reopened (new output or docks, rare)
        x, y, width, height = geometry
        eww("open", "bar", "--pos", f"{x}x{y}", "--size", f"{width}x{height}")
        last_geometry = geometry
    elif hidden:
        xdotool_bar("windowmap")
    hidden = False


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
