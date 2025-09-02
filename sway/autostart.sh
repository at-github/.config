#!/bin/sh

# Choisit un fond et génère les couleurs
wal -i /usr/share/backgrounds/wallpapers/3840x2160 -e

# Tue tout ancien swaybg
pkill -x swaybg 2>/dev/null

# Applique le fond choisi par wal
swaybg -i "$(head -n 1 ~/.cache/wal/wal)" -m fill &
