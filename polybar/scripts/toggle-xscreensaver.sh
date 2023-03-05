#!/bin/bash
if [ "$(pidof xscreensaver)" ]
then
  xscreensaver-command --exit
  pidof xscreensaver
  notify-send "Screensaver Disabled"
else
   xscreensaver -no-splash &
   notify-send "Screensaver Enabled"
fi
