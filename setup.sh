#!/data/data/com.termux/files/usr/bin/bash
set -e

if [ -z "${PREFIX:-}" ] || [ ! -d "$PREFIX" ]; then
    echo "Please run this setup inside the main Termux app, not inside PRoot."
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$PREFIX/bin"

echo "Installing PY-OS Full requirements..."
pkg update -y
pkg install -y x11-repo
pkg install -y git python python-tkinter termux-x11-nightly procps busybox

mkdir -p "$BIN_DIR"
printf -v PROJECT_PATH_Q '%q' "$PROJECT_DIR"

cat > "$BIN_DIR/py-os" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
PROJECT_DIR=$PROJECT_PATH_Q
if [ ! -f "\$PROJECT_DIR/cli/main.py" ]; then
    echo "PY-OS CLI files not found: \$PROJECT_DIR/cli/main.py"
    exit 1
fi
cd "\$PROJECT_DIR/cli"
exec python main.py "\$@"
EOF

for command_name in py-os-update py-os-gui-update py-os-full-update; do
    cat > "$BIN_DIR/$command_name" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
PROJECT_DIR=$PROJECT_PATH_Q
if [ ! -d "\$PROJECT_DIR/.git" ]; then
    echo "PY-OS Full Git folder not found: \$PROJECT_DIR"
    exit 1
fi
cd "\$PROJECT_DIR"
git pull --ff-only
EOF
done

cat > "$BIN_DIR/py-os-gui" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
PROJECT_DIR=$PROJECT_PATH_Q
if [ ! -f "\$PROJECT_DIR/gui/start.sh" ]; then
    echo "PY-OS GUI files not found: \$PROJECT_DIR/gui/start.sh"
    exit 1
fi
exec bash "\$PROJECT_DIR/gui/start.sh" "\$@"
EOF

chmod +x "$BIN_DIR/py-os" "$BIN_DIR/py-os-update" \
    "$BIN_DIR/py-os-gui" "$BIN_DIR/py-os-gui-update" \
    "$BIN_DIR/py-os-full-update"

echo
echo "PY-OS Full setup complete!"
echo "Commands installed:"
echo "  py-os               - start the terminal interface"
echo "  py-os-update        - update the combined project"
echo "  py-os-gui            - start the graphical desktop"
echo "  py-os-gui-update     - update the combined project"
echo "  py-os-full-update    - update the entire PY-OS Full project"
echo
echo "For the desktop, open the Termux:X11 Android app first."
