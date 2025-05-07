#!/bin/bash

DEVICE="/dev/video0"

if lsof "$DEVICE" &>/dev/null; then
    echo "%{F#FF0000}●%{F-}"  # point rouge
else
    echo "%{F#333333}●%{F-}"  # point rouge
fi
