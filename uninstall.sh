#!/bin/zsh
# This script is the uninstallation script of dlmenu
echo "Removing the shell function from ~/.zshrc..."
if [ -f ~/.zshrc ]; then
  sed -i.bak '/# DLMenu start/,/# DLMenu end/d' ~/.zshrc && rm -f ~/.zshrc.bak
fi
echo "Removing ~/dlmenu and ~/.dlmenu ..."
rm -rf "$HOME/dlmenu" "$HOME/.dlmenu"
echo "Uninstallation finished! Reopen the terminal to apply."
