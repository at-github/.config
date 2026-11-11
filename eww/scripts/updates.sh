#!/usr/bin/env bash
# Pending pacman, AUR and flatpak updates
#   updates.sh                  print icons and counts as JSON (for defpoll), "!" on error
#   updates.sh upgrade SOURCE   upgrade SOURCE (pacman, aur or flatpak) in kitty, then refresh
#
# Icons: Arch logo for pacman, account-group for the AUR, package for flatpak

lines() { grep -c .; }

pacman_count() {
  local out
  out=$(checkupdates 2>/dev/null)
  case $? in
    0) printf '%s\n' "$out" | lines ;;
    2) echo 0 ;; # No updates
    *) echo '!' ;;
  esac
}

aur_count() {
  local out err
  err=$(mktemp)
  out=$(yay -Qua 2>"$err")
  # yay fails when nothing is pending too: only its error messages tell an error
  if [ -n "$out" ]; then
    printf '%s\n' "$out" | lines
  elif [ -s "$err" ]; then
    echo '!'
  else
    echo 0
  fi
  rm -f "$err"
}

flatpak_count() {
  local out
  out=$(flatpak remote-ls --updates 2>/dev/null) || { echo '!'; return; }
  printf '%s\n' "$out" | lines
}

print_counts() {
  printf '[{"source":"pacman","name":"pacman","icon":"%s","count":"%s"},' $'\U000f08c7' "$(pacman_count)"
  printf '{"source":"aur","name":"AUR","icon":"%s","count":"%s"},' $'\U000f0849' "$(aur_count)"
  printf '{"source":"flatpak","name":"flatpak","icon":"%s","count":"%s"}]\n' $'' "$(flatpak_count)"
}

case "$1" in
  upgrade)
    case "$2" in
      pacman) command=(sudo pacman -Syyu) ;;
      aur) command=(yay -Sua) ;;
      flatpak) command=(flatpak update) ;;
      *) exit 1 ;;
    esac
    # eww kills click commands after 200ms: run detached
    setsid -f bash -c 'kitty -e "${@:2}"; eww update updates="$("$1")"' \
      _ "$0" "${command[@]}" >/dev/null 2>&1
    ;;
  *)
    print_counts
    ;;
esac
