# .zshrc
autoload -U promptinit; promptinit
prompt spaceship

SPACESHIP_PROMPT_ORDER=(
  dir           # Current directory section
  git           # Git section (git_branch + git_status)
  line_sep      # Line break
  battery       # Battery level and status
  jobs          # Background jobs indicator
  char          # Prompt character
)

SPACESHIP_PROMPT_ADD_NEWLINE=false
SPACESHIP_PROMPT_SEPARATE_LINE=true
SPACESHIP_CHAR_SYMBOL='➜ '
SPACESHIP_USER_SHOW=false
SPACESHIP_HOST_SHOW=true
SPACESHIP_DIR_PREFIX=' '
SPACESHIP_GIT_SYMBOL=''

SPACESHIP_GIT_STATUS_SHOW=true

neofetch

source ~/dotfiles/.zsh/alias.zsh
source ~/dotfiles/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/dotfiles/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh

#if type brew &>/dev/null; then
    #FPATH=$(brew --prefix)/share/zsh-completions:$FPATH

    #autoload -Uz compinit
    #compinit
#fi

