#!/usr/bin/env bash

# Terminate already running bar instances
# If all your bars have ipc enabled, you can use 
polybar-msg cmd quit
# Otherwise you can use the nuclear option:
# killall -q polybar

# Launch main and workspaces
echo "---" | tee -a /tmp/polybar-main.log /tmp/polybar-dock.log
polybar -r main 2>&1 | tee -a /tmp/polybar-main.log & disown
polybar -r dock 2>&1 | tee -a /tmp/polybar-dock.log & disown

echo "Bars launched..."
