# Fig pre block. Keep at the top of this file.
[[ -f "$HOME/.fig/shell/zshrc.pre.zsh" ]] && builtin source "$HOME/.fig/shell/zshrc.pre.zsh"
## .zshrc
#autoload -U promptinit; promptinit
#prompt spaceship

#SPACESHIP_PROMPT_ORDER=(
  #dir           # Current directory section
  #git           # Git section (git_branch + git_status)
  #line_sep      # Line break
  #battery       # Battery level and status
  #jobs          # Background jobs indicator
  #char          # Prompt character
#)

#SPACESHIP_PROMPT_ADD_NEWLINE=true
#SPACESHIP_PROMPT_SEPARATE_LINE=false
#SPACESHIP_CHAR_SYMBOL='➜ '
#SPACESHIP_USER_SHOW=false
#SPACESHIP_HOST_SHOW=true
#SPACESHIP_DIR_PREFIX=' '
#SPACESHIP_GIT_SYMBOL=''

#SPACESHIP_GIT_STATUS_SHOW=true

#neofetch

source ~/dotfiles/.zsh/alias.zsh
source ~/dotfiles/.zsh/nnn.zsh
#source ~/dotfiles/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
#source ~/dotfiles/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh

#ZSH_AUTOSUGGEST_STRATEGY=(history completion)
#bindkey '^ ' autosuggest-accept

#zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'

##if type brew &>/dev/null; then
    ##FPATH=$(brew --prefix)/share/zsh-completions:$FPATH

    ##autoload -Uz compinit
    ##compinit
##fi

# Fig post block. Keep at the bottom of this file.
[[ -f "$HOME/.fig/shell/zshrc.post.zsh" ]] && builtin source "$HOME/.fig/shell/zshrc.post.zsh"
