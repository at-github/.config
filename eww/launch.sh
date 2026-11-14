#!/usr/bin/env bash
# Restart the vertical bar (eww daemon + i3 driver)

pkill -f eww/scripts/i3-listener.py
eww kill
# Classic scrollbars: always shown while the workspaces overflow (GTK hides
# overlay scrollbars when idle)
GTK_OVERLAY_SCROLLING=0 eww daemon
exec "$HOME/.config/eww/scripts/i3-listener.py"
