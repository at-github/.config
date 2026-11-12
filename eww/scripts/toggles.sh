#!/usr/bin/env bash
# Redshift, microphone and xscreensaver states
#   toggles.sh                print the states as JSON, then again on each change (for deflisten)
#   toggles.sh redshift       start or stop redshift
#   toggles.sh xscreensaver   start or stop xscreensaver
#
# Microphone changes come from `pactl subscribe`; redshift and xscreensaver are
# toggled by the bar, which updates `toggles` itself. A slow refresh catches
# the other changes (a service stopped or crashed outside the bar).
#
# Redshift shows an empty or full lightbulb

print_states() {
  redshift_active=false
  redshift_icon=$'\U000f0336'
  if systemctl --user is-active --quiet redshift; then
    redshift_active=true
    redshift_icon=$'\U000f0335'
  fi

  mic_muted=false
  mic_icon=$''
  if LC_ALL=C pactl get-source-mute @DEFAULT_SOURCE@ | grep -q 'Mute: yes'; then
    mic_muted=true
    mic_icon=$''
  fi

  # In use when an application is recording from any source
  mic_in_use=false
  [ -n "$(pactl list short source-outputs)" ] && mic_in_use=true

  xscreensaver_active=false
  xscreensaver_icon=$'\U000f180d'
  if pidof xscreensaver >/dev/null; then
    xscreensaver_active=true
    xscreensaver_icon=$'\U000f042f'
  fi

  printf '{"redshift_active":%s,"redshift_icon":"%s","mic_muted":%s,"mic_icon":"%s","mic_in_use":%s,"xscreensaver_active":%s,"xscreensaver_icon":"%s"}\n' \
    "$redshift_active" "$redshift_icon" "$mic_muted" "$mic_icon" "$mic_in_use" "$xscreensaver_active" "$xscreensaver_icon"
}

REFRESH_SECONDS=30

# Print the states at start, then each time they change
listen() {
  local last="" states line status fd
  while true; do
    # Sources (mute, default) and source outputs (recording applications)
    exec {fd}< <(LC_ALL=C pactl subscribe 2>/dev/null)
    while true; do
      states=$(print_states)
      if [ "$states" != "$last" ]; then
        printf '%s\n' "$states"
        last=$states
      fi
      # Wait for a source event, or for the slow refresh (read timeout)
      while true; do
        read -r -t "$REFRESH_SECONDS" -u "$fd" line
        status=$?
        [ "$status" -ne 0 ] && break
        [[ $line == *" on source"* || $line == *" on server"* ]] && break
      done
      # pactl ended (audio server restarted): subscribe again
      [ "$status" -ne 0 ] && [ "$status" -le 128 ] && break
    done
    exec {fd}<&-
    sleep 1
  done
}

# After a click: update the bar as soon as the state changed, at most 1s later
# (detached, eww kills click commands after 200ms)
refresh_after_click() {
  local before
  before=$(print_states)
  setsid -f bash -c '
    for ((i = 0; i < 20; i++)); do
      states=$("$0" states)
      [ "$states" != "$1" ] && break
      sleep 0.05
    done
    eww update toggles="$states"' "$0" "$before" >/dev/null 2>&1
}

case "$1" in
  redshift)
    refresh_after_click
    if systemctl --user is-active --quiet redshift; then
      systemctl --user stop redshift
    else
      systemctl --user start redshift
    fi
    ;;
  xscreensaver)
    refresh_after_click
    if pidof xscreensaver >/dev/null; then
      xscreensaver-command -exit
    else
      # eww kills click commands after 200ms: run detached
      setsid -f xscreensaver -no-splash >/dev/null 2>&1
    fi
    ;;
  states)
    print_states
    ;;
  *)
    listen
    ;;
esac
