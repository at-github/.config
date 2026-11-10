#!/usr/bin/env bash
# Calendar window actions
#   calendar.sh toggle               open or close the calendar (click on the clock)
#   calendar.sh day DAY MONTH YEAR   a day was selected (MONTH counts from 0, like GTK)
#   calendar.sh open YYYYMMDD        show that date in Evolution's agenda
#
# GTK also selects a day when the month changes (arrows), so the shown month is
# remembered: a selection in another month is only a navigation.

state="${XDG_RUNTIME_DIR:-/tmp}/eww-calendar-month"
calendar_title='^Agenda — Evolution$'

case "$1" in
  toggle)
    # The calendar always opens on the current month
    date +%Y-%m >"$state"
    eww open --toggle calendar
    ;;
  day)
    shown=$(printf '%04d-%02d' "$4" $(($3 + 1)))
    if [ "$shown" != "$(cat "$state" 2>/dev/null)" ]; then
      echo "$shown" >"$state"
      exit 0
    fi

    eww close calendar
    # eww kills click commands after 200ms: open the agenda detached
    setsid -f "$0" open "$(printf '%04d%02d%02d' "$4" $(($3 + 1)) "$2")" >/dev/null 2>&1
    ;;
  open)
    uri="calendar:///?startdate=$2"
    had_calendar=$(xdotool search --name "$calendar_title")
    # xdg-open waits for Evolution when it starts it
    setsid -f xdg-open "$uri" >/dev/null 2>&1
    # Without a calendar window, Evolution creates one and loses the date: send it again
    if [ -z "$had_calendar" ]; then
      for _ in $(seq 30); do
        xdotool search --name "$calendar_title" >/dev/null && break
        sleep 0.5
      done
      sleep 1
      setsid -f xdg-open "$uri" >/dev/null 2>&1
    fi
    ;;
esac
