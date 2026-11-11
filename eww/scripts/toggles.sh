#!/usr/bin/env bash
# Redshift, microphone and xscreensaver states
#   toggles.sh                print the states as JSON (for defpoll)
#   toggles.sh redshift       start or stop redshift
#   toggles.sh xscreensaver   start or stop xscreensaver
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

case "$1" in
  redshift)
    if systemctl --user is-active --quiet redshift; then
      systemctl --user stop redshift
    else
      systemctl --user start redshift
    fi
    ;;
  xscreensaver)
    if pidof xscreensaver >/dev/null; then
      xscreensaver-command -exit
    else
      # eww kills click commands after 200ms: run detached
      setsid -f xscreensaver -no-splash >/dev/null 2>&1
    fi
    ;;
  *)
    print_states
    ;;
esac
