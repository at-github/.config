#!/usr/bin/env bash
# Restart the vertical bar (eww daemon + i3 driver)

pkill -f eww/scripts/i3-listener.py
eww kill
eww daemon
exec "$HOME/.config/eww/scripts/i3-listener.py"
