# Tmux

## Prefix

The chosen prefix is `a`, so use `<C-a>` to launch tmux commands.

## Shortcuts

- `prefix r` to reload configuration
- `prefix m` to toggle mouse support, by default is enable
- `v` to select text in tmux copy mode
- `y` to copy selected text in tmux copy mode
- `<C-↑→↓←>` to move into panes, same commands in *copy mode*

## Tmuxinator

To get the reference of the current nice layout,
type this tmux command:
`display-message -p "#{window_layout}`

Then copy paste the message into layout section of the Tmuxinator project:
```
windows:
  - editor:
      layout: 1520,191x69,0,0{95x69,0,0,0,95x69,96,0[95x34,96,0,1,95x34,96,35,2]}
      panes:
        - dc up -d
        - e src
        - e notes.md
```

Other command it's default tmux binding.
