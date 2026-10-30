# This script is the installation script of dlmenu
dir=$(pwd)
cd "$HOME" || exit 1
echo "Cloning the repository..."
git clone https://github.com/huangdihd/dlmenu
cd dlmenu || exit 1
echo "Creating virtual environment..."
python3 -m venv ./.venv
echo "Activating virtual environment..."
. ./.venv/bin/activate
echo "Installing dependencies..."
pip install -r ./requirements.txt
cat << EOF >> ~/.zshrc
# DLMenu start
dlmenu() {
  source "$(pwd)/.venv/bin/activate"
  python3 "$(pwd)/main.py" "\$@"
  local status=\$?
  deactivate
  return \$status
}
# DLMenu end
EOF
echo "Installation finished!"
echo "Reopen the terminal and use command \"dlmenu\" to see what's for lunch!"
cd "$dir" || exit
