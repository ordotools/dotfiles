# Fig pre block. Keep at the top of this file.
. "$HOME/.fig/shell/zshrc.pre.zsh"

export ZSH="$HOME/.oh-my-zsh"

COMPLETION_WAITING_DOTS="true"

plugins=(
  git 
  git-flow-completion
)
  
source $ZSH/oh-my-zsh.sh

source "$HOME/dotfiles/alias.zsh"

alias v="~/bin/v.sh"

clear
# Fig post block. Keep at the bottom of this file.
. "$HOME/.fig/shell/zshrc.post.zsh"
