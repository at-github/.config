#!/usr/bin/env bash
# On-screen display for volume and media keys, rendered by eww (window `osd`
# in ~/.config/eww/eww.yuck, look in eww.scss). Every key press updates the
# same window: current track (if any, with its cover), then the volume glyph
# and a bar. The
# window closes TIMEOUT after the last key press.
#
# Usage:
#   osd.sh volume up|down|mute
#   osd.sh media [playerctl options] play-pause|next|previous
#   (media keys drive Kodi when it plays something, see kodi.py)

TIMEOUT=1500ms
KODI="$(dirname "$0")/kodi.py"
# Field separator of the player info (unit separator): unlike a tab, `read`
# keeps the empty fields
SEP=$'\x1f'
# Covers downloaded from http(s) URLs and square covers, cleared with the session
ART_CACHE="${XDG_RUNTIME_DIR:-/tmp}/osd-art"
# Side of the square covers, in pixels (same as eww.yuck)
COVER_SIZE=120

# Nerd Font (Font Awesome) glyphs
GLYPH_VOLUME_HIGH=$'\uF028'
GLYPH_VOLUME_LOW=$'\uF027'
GLYPH_VOLUME_OFF=$'\uF026'
GLYPH_VOLUME_MUTED=$'\uEEE8'
GLYPH_PLAY=$'\uF04B'
GLYPH_PAUSE=$'\uF04C'
GLYPH_STOP=$'\uF04D'

# Text lines of the media part, in characters (the eww font is monospace). Long
# titles are wrapped on words over TITLE_LINES lines, then ellipsized.
LINE_CHARS=44
# The cover (eww.yuck, eww.scss) leaves less room to the text
COVER_LINE_CHARS=38
TITLE_LINES=2
ELLIPSIS=$'\u2026'

# Cut a text to $2 characters, ending with an ellipsis when it is longer
truncate_text() {
    local text="$1" max="$2"
    if [ "${#text}" -le "$max" ]; then
        printf '%s' "$text"
    else
        printf '%s%s' "${text:0:max-1}" "$ELLIPSIS"
    fi
}

# Print a text wrapped on words, one line per output line, at most $2 lines of
# LINE_CHARS characters; the last line is ellipsized if text remains
wrap_text() {
    local text="$1" max_lines="$2"
    local line="" count=0 word rest i
    local -a words
    read -ra words <<<"$text"
    for ((i = 0; i < ${#words[@]}; i++)); do
        word="${words[i]}"
        if [ -z "$line" ]; then
            line="$word"
        elif [ $((${#line} + 1 + ${#word})) -le "$LINE_CHARS" ]; then
            line+=" $word"
        else
            count=$((count + 1))
            if [ "$count" -eq "$max_lines" ]; then
                # Last allowed line: keep the remaining words and ellipsize
                rest="${words[*]:i}"
                truncate_text "$line $rest" "$LINE_CHARS"
                printf '\n'
                return
            fi
            truncate_text "$line" "$LINE_CHARS"
            printf '\n'
            line="$word"
        fi
    done
    [ -n "$line" ] && truncate_text "$line" "$LINE_CHARS" && printf '\n'
}

# Kodi JSON-RPC port answers (much cheaper than starting python or pgrep)
kodi_running() {
    (: <>/dev/tcp/127.0.0.1/9090) 2>/dev/null
}

# Print "status<SEP>title<SEP>artist<SEP>cover URL" of the current player,
# Kodi first. Arguments: playerctl options selecting the player.
player_info() {
    kodi_running && "$KODI" status 2>/dev/null && return
    playerctl "$@" metadata \
        --format "{{ status }}$SEP{{ title }}$SEP{{ artist }}$SEP{{ mpris:artUrl }}" 2>/dev/null
}

# Print the local file of a cover URL: file:// URLs and paths as is, http(s)
# URLs downloaded once into ART_CACHE; nothing when it is not available
source_cover_file() {
    local url="$1" file path
    case "$url" in
        file://*)
            # Percent-decoded path
            path="${url#file://}"
            printf -v file '%b' "${path//%/\\x}"
            ;;
        /*) file=$url ;;
        http://* | https://*)
            file="$ART_CACHE/$(printf '%s' "$url" | sha1sum | cut -d' ' -f1)"
            if [ ! -s "$file" ]; then
                mkdir -p "$ART_CACHE"
                curl -sfL --max-time 1 -o "$file.part" "$url" && mv "$file.part" "$file" \
                    || { rm -f "$file.part"; return; }
            fi
            ;;
        *) return ;;
    esac
    [ -r "$file" ] && printf '%s' "$file"
}

# Print a square COVER_SIZE version of a cover URL (center crop of the
# original, video thumbnails being 16:9), made once per image content;
# nothing when it is not available
cover_file() {
    local source square
    source=$(source_cover_file "$1") || return
    square="$ART_CACHE/square-$(sha1sum <"$source" | cut -d' ' -f1).png"
    if [ ! -s "$square" ]; then
        mkdir -p "$ART_CACHE"
        magick "$source" -resize "${COVER_SIZE}x${COVER_SIZE}^" -gravity center \
            -extent "${COVER_SIZE}x${COVER_SIZE}" "$square.part.png" \
            && mv "$square.part.png" "$square" || { rm -f "$square.part.png"; return 1; }
    fi
    printf '%s' "$square"
}

# Set status_glyph, title (wrapped, newline-separated), artist and cover (local
# file) of the current player; all empty when no player is active or when it is
# stopped without a track. Arguments: playerctl options selecting the player.
media_info() {
    local status raw_title raw_artist raw_cover
    status_glyph="" title="" artist="" cover=""
    IFS=$SEP read -r status raw_title raw_artist raw_cover < <(player_info "$@") || return
    [ "$status" = Stopped ] && [ -z "$raw_title" ] && return

    cover=$(cover_file "$raw_cover")
    # Seen by wrap_text and truncate_text (bash variables are dynamically scoped)
    local LINE_CHARS=$LINE_CHARS
    [ -n "$cover" ] && LINE_CHARS=$COVER_LINE_CHARS

    case "$status" in
        Playing) status_glyph=$GLYPH_PLAY ;;
        Paused)  status_glyph=$GLYPH_PAUSE ;;
        *)       status_glyph=$GLYPH_STOP ;;
    esac
    title=$(wrap_text "${raw_title:-$status}" "$TITLE_LINES")
    [ -n "$raw_artist" ] && artist=$(truncate_text "$raw_artist" "$LINE_CHARS")
}

# Show the OSD. Arguments: playerctl options selecting the player.
show_osd() {
    # Last line looks like: "Front Right: Playback 52441 [80%] [on]"
    local state level g
    state=$(amixer -D pulse get Master | tail -n 1)
    level=$(grep -oP '\[\K[0-9]+(?=%\])' <<<"$state")

    if grep -q '\[off\]' <<<"$state"; then
        g=$GLYPH_VOLUME_MUTED
        # Empty bar so muting is obvious at a glance
        level=0
    else
        if [ "$level" -eq 0 ]; then
            g=$GLYPH_VOLUME_OFF
        elif [ "$level" -lt 50 ]; then
            g=$GLYPH_VOLUME_LOW
        else
            g=$GLYPH_VOLUME_HIGH
        fi
    fi

    local status_glyph title artist cover
    media_info "$@"

    # media: [] without a track, [{status_glyph, title, artists, covers}]
    # otherwise, artists being [] or [artist] and covers [] or [file] (lists,
    # since eww sizes windows with hidden widgets too)
    local osd
    osd=$(jq -nc \
        --arg status_glyph "$status_glyph" --arg title "$title" --arg artist "$artist" \
        --arg cover "$cover" \
        --arg volume_glyph "$g" --argjson level "$level" \
        '{media: (if $title == "" then [] else
                    [{$status_glyph, $title,
                      artists: (if $artist == "" then [] else [$artist] end),
                      covers: (if $cover == "" then [] else [$cover] end)}]
                  end),
          $volume_glyph, $level}')
    eww update osd="$osd"
    # Opening an open window recreates it (so it also shrinks to its content)
    # and restarts its close timer
    eww open osd --duration "$TIMEOUT"
}

volume_osd() {
    case "$1" in
        up)   amixer -q -D pulse sset Master 5%+ ;;
        down) amixer -q -D pulse sset Master 5%- ;;
        mute) amixer -q -D pulse sset Master toggle ;;
        *)    echo "unknown volume action: $1" >&2; exit 1 ;;
    esac
    show_osd
}

media_osd() {
    # The last argument is the playerctl command, the others select the player
    local action="${*: -1}"
    local player_opts=("${@:1:$#-1}")

    local before i
    before=$(player_info "${player_opts[@]}")

    # Kodi first when it has an active player, MPRIS players otherwise
    { kodi_running && "$KODI" "$action" 2>/dev/null; } \
        || playerctl "${player_opts[@]}" "$action" || exit 0

    # Players update status/metadata asynchronously: show the OSD as soon as
    # they changed, at most 0.5s later
    for ((i = 0; i < 10; i++)); do
        [ "$(player_info "${player_opts[@]}")" != "$before" ] && break
        sleep 0.05
    done
    show_osd "${player_opts[@]}"
}

case "$1" in
    volume) shift; volume_osd "$@" ;;
    media)  shift; media_osd "$@" ;;
    *)      echo "usage: $0 volume up|down|mute | media [playerctl options] <command>" >&2; exit 1 ;;
esac
