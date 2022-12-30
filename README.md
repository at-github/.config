# .config

## Tmux

See : [tmux/README](./tmux/README.md)

## Neovim

See : [nvim/README](https://github.com/at-github/nvim/blob/master/README.md)

## Zsh

See : [zsh/README](./zsh/README.md)

## Git

See : [git/README](./git/README.md)

## Kitty

See : [kitty/README](./kitty/README.md)

## Testing

Launch proper container with copied Makefile

```shell
make docker-build # Build container
make docker-jump # Jump into container
# Makefile was copied into the container during the build
# So we can edit it & see changes without commit & push

# Inside the container:
make zsh # Install zsh config
make neovim # Install neovim config
```
