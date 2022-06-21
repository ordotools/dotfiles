#! /bin/zsh
# Adjust init.vim from anywhere
# This is not working right now!!!
echo "Working on opening nvim..."
lvar=`cd ~/.config/nvim/`
var=`nvim ~/.config/nvim/init.vim`
exit $var
