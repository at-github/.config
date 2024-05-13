#!/bin/bash
if [ $(playerctl -p Blanket status) == "Playing" ]
then
  echo " 󰔢"
else
  echo " 󰨚"
fi
