#!/usr/bin/env bash
# Relance la barre verticale (daemon eww + pilote i3)

pkill -f eww/scripts/i3-listener.py
eww kill
eww daemon
exec "$HOME/.config/eww/scripts/i3-listener.py"
