#!/bin/zsh

function latex_styles_update() {
   cd ~/Library/texmf/tex/
   git pull
   echo "LaTeX styles have been updated"
   cd -
}

function sendit() {
   git add . && git commit -m '$1' && git push
}
