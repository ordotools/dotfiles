# Fig pre block. Keep at the top of this file.
. "$HOME/.fig/shell/zshrc.pre.zsh"

export ZSH="/Users/gregbarnes/.oh-my-zsh"

COMPLETION_WAITING_DOTS="true"

plugins=(
  git 
  git-flow-completion
)
  
source $ZSH/oh-my-zsh.sh

source "alias"
alias v="~/bin/v.sh" # access newvimwith v

clear
# Fig post block. Keep at the bottom of this file.
. "$HOME/.fig/shell/zshrc.post.zsh"
