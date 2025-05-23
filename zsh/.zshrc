source "$ZDOTDIR/.aliases"

# If you come from bash you might have to change your $PATH.
if [ -d /sbin ]; then
    PATH=/sbin:$PATH
fi

#Source this path so some program like nginx is autocompleted
if [ -d /usr/sbin ]; then
    PATH=/usr/sbin:$PATH
fi

#Snap
if [ -d /snap/bin ]; then
    PATH=/snap/bin:$PATH
fi

# Locally binaries
if [ -d ${USER_BIN} ]; then
    PATH=$PATH:${USER_BIN}
fi

if [ -d ${TA_SOURCE}/git ]; then
    PATH=${TA_SOURCE}/git/bin:$PATH
fi

if [ -d ${HOME}/.config/composer/vendor/bin ]; then
    PATH=${HOME}/.config/composer/vendor/bin:$PATH
fi

if [ -d ${HOME}/.local/share/gem/ruby/3.0.0/bin ]; then
    PATH=${HOME}/.local/share/gem/ruby/3.0.0/bin:$PATH
fi

if [ -f ${HOME}/.zshrc.local ]; then
  source ${HOME}/.zshrc.local
fi

if [ -f $HOME/.rvm/scripts/completion ]; then
  source $HOME/.rvm/scripts/completion
fi

if [ -f $HOME/.rvm/scripts/rvm ]; then
  source $HOME/.rvm/scripts/rvm
fi

# Python env/venv
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

# Node
if [ -f /usr/share/nvm/init-nvm.sh ]; then
  source /usr/share/nvm/init-nvm.sh
fi

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.

# Poetry
#
# mkdir $ZSH_CUSTOM/plugins/poetry
# poetry completions zsh > $ZSH_CUSTOM/plugins/poetry/_poetry

plugins=(\
  colored-man-pages \
  git \
  git-prompt \
  history-substring-search \
  node \
  poetry \
  rails \
  ruby \
  vi-mode \
  wp-cli \
  zoxide \
  zsh-autosuggestions \
  zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh
# User configuration

# history-substring-search
bindkey '^P' history-substring-search-up
bindkey '^N' history-substring-search-down
bindkey -M vicmd 'k' history-substring-search-up
bindkey -M vicmd 'j' history-substring-search-down

# vi-mode
VI_MODE_SET_CURSOR=true
MODE_INDICATOR="%F{white}+%f"
INSERT_MODE_INDICATOR="%F{yellow}+%f"

# zsh-autosuggestions
bindkey '^ ' autosuggest-accept

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.

# COLORS

# Import colorscheme from 'wal' asynchronously
# &   # Run the process in the background.
# ( ) # Hide shell job control messages.
# Not supported in the "fish" shell.
if [ -f ${HOME}/.cache/wal/sequences ]; then
  (\cat ${HOME}/.cache/wal/sequences &)
fi

# Alternative (blocks terminal for 0-3ms)
# cat ~/.cache/wal/sequences

# To add support for TTYs this line can be optionally added.
if [ -f ${HOME}/.cache/wal/colors-tty.sh ]; then
  source ${HOME}/.cache/wal/colors-tty.sh
fi

if [ -f ${HOME}/.cache/wal/colors.sh ]; then
  source ${HOME}/.cache/wal/colors.sh
fi

if [ -f ${HOME}/.cache/wal/colors.sh ]; then
  source ${HOME}/.cache/wal/colors.sh
fi

source <(fzf --zsh)

RESET=%f

LTGRAY=244
GRAY=234
CYAN=37
GREEN=64
MAGENTA=125
ORANGE=166
YELLOW=136
RED=160

BORANGE="$(tput setab $ORANGE)"

FLTGRAY='#999999'
FGRAY='#666666'
FGREEN='#5ec24c'
FMAGENTA='#813181'
FRED='#EE2222'
FYELLOW='#c7c71b'

# PROMPT

DOCKER_STATUS=''
if [ -f /.dockerenv ]; then
  DOCKER_STATUS=' '
fi

if [[ $(whoami) == 'root' ]]; then
  PROMPT=${DOCKER_STATUS}%{$BORANGE%}%{$FGRAY%}
else
  PROMPT=${DOCKER_STATUS}%F{${color2-${FYELLOW}}%}
fi

PROMPT+=%F{${color4:-${FYELLOW}}}%n%{$RESET%}
PROMPT+=%F{${color3:-${FGRAY}}}' @ '%F{${color4:-${FYELLOW}}%}%M$'%{$RESET%}\n'
PROMPT+=%F{${color1:-${FLTGRAY}}}'%$PR_PWDLEN<...<%~%<< '%{$RESET%}$'\n'
#jobs
PROMPT+=%(1j.%F{${color5:-${FYELLOW}}}'%1{⚒ %}%j' %{$RESET%}.)
#last returned code
PROMPT+=%(?..%F{${color5:-${FYELLOW}}}'%1{ %}%1{%?%}' %{$RESET%})
PROMPT+=$'%F{${color4:-${FYELLOW}}}\n%1{➜%} %{$RESET%}'

RPROMPT='%F{${color1:-${FLTGRAY}}}$(git_super_status)'
ZSH_THEME_GIT_PROMPT_PREFIX=""
ZSH_THEME_GIT_PROMPT_SUFFIX=""
ZSH_THEME_GIT_PROMPT_SEPARATOR=" %F{$FLTGRAY%}|"
ZSH_THEME_GIT_PROMPT_BRANCH=" "
ZSH_THEME_GIT_PROMPT_STASHED=" %F{$FYELLOW%}%{⚑%G%}"
ZSH_THEME_GIT_PROMPT_STAGED=" %F{$FGREEN%}%{✓%G%}"
ZSH_THEME_GIT_PROMPT_CONFLICTS=" %F{$FRED%}%{⚠%G%}"
ZSH_THEME_GIT_PROMPT_CHANGED=" %F{$FYELLOW%}%{✹%G%}"
ZSH_THEME_GIT_PROMPT_UNTRACKED=" %F{$FMAGENTA%}%{•%G%}"
ZSH_THEME_GIT_PROMPT_CLEAN=" %F{$FYELLOW%}%{☮ %G%}"
ZSH_THEME_GIT_PROMPT_BEHIND=" %{↓%G%}"
ZSH_THEME_GIT_PROMPT_AHEAD=" %{↑%G%}"
