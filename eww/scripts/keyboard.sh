#!/usr/bin/env bash
# Print the keyboard layout and Caps Lock state as JSON (for defpoll)

query=$(setxkbmap -query)
layout=$(awk '/^variant:/ {print $2}' <<<"$query")
[ -n "$layout" ] || layout=$(awk '/^layout:/ {print $2}' <<<"$query")

caps=false
xset q | grep -q 'Caps Lock: *on' && caps=true

printf '{"layout":"%s","caps":%s}\n' "$layout" "$caps"
