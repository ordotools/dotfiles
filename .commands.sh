#!/bin/zsh

function latex_styles_update() {
   cd ~/Library/texmf/tex/
   git pull
   echo "LaTeX styles have been updated"
   cd -
}
