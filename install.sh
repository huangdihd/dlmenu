# This script is the installation script of dlmenu
dir=$(pwd)
cd "$HOME" || exit 1
if [ -d "$HOME/dlmenu/.git" ]; then
  echo "Updating the existing installation..."
  git -C "$HOME/dlmenu" pull --ff-only || exit 1
else
  echo "Cloning the repository..."
  git clone https://github.com/huangdihd/dlmenu "$HOME/dlmenu" || exit 1
fi
cd "$HOME/dlmenu" || exit 1
echo "Creating virtual environment..."
python3 -m venv ./.venv || exit 1
echo "Installing dependencies..."
./.venv/bin/python3 -m pip install -r ./requirements.txt || exit 1
# Remove an old shell function (older versions activated the venv and used the
# read-only zsh variable "status", which left the venv active after an error).
if [ -f "$HOME/.zshrc" ]; then
  sed -i.bak '/# DLMenu start/,/# DLMenu end/d' "$HOME/.zshrc" && rm -f "$HOME/.zshrc.bak"
fi
cat << EOF >> "$HOME/.zshrc"
# DLMenu start
dlmenu() {
  "$HOME/dlmenu/.venv/bin/python3" "$HOME/dlmenu/main.py" "\$@"
}
# DLMenu end
EOF
echo "Installation finished!"
echo "Reopen the terminal and use command \"dlmenu\" to see what's for lunch!"
cd "$dir" || exit
