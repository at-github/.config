#!/usr/bin/env bash
# Print redshift, microphone and xscreensaver states as JSON (for defpoll)
# Same icons as the polybar modules

redshift_icon=$''
systemctl --user is-active --quiet redshift && redshift_icon=$''

mic_icon=$''
if LC_ALL=C pactl get-source-mute @DEFAULT_SOURCE@ | grep -q 'Mute: yes'; then
  mic_icon=$''
fi

# In use when an application is recording from any source
mic_in_use=false
[ -n "$(pactl list short source-outputs)" ] && mic_in_use=true

xscreensaver_icon=$'\U000f180d'
pidof xscreensaver >/dev/null && xscreensaver_icon=$'\U000f042f'

printf '{"redshift_icon":"%s","mic_icon":"%s","mic_in_use":%s,"xscreensaver_icon":"%s"}\n' \
  "$redshift_icon" "$mic_icon" "$mic_in_use" "$xscreensaver_icon"
