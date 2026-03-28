#!/bin/bash

[ -f $HOME/.cache/wal/colors.sh ] && source $HOME/.cache/wal/colors.sh

tmux set -g status-style "bg=${background:-colour235},fg=${color7:-colour130}"

tmux set -g window-status-style "fg=${color7:-colour244}"
tmux set -g window-status-current-style "fg=${foreground:-colour235},bg=${color10:-colour136}"
tmux set -g status-left-style "fg=${color8:-colour244}"
tmux set -g status-right-style "fg=${color8:-colour244}"

tmux set -g pane-border-style "fg=${background:-colour235}"
tmux set -g pane-active-border-style "fg=${background:-colour240}"

tmux set -g message-style "bg=${color0:-colour235},fg=${color6:-colour166}"

tmux set -g display-panes-active-colour "${color4:-colour33}"
tmux set -g display-panes-colour "${color5:-colour166}"

tmux set -g clock-mode-colour "${color2:-colour40}"
