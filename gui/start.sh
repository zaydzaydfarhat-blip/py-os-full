#!/data/data/com.termux/files/usr/bin/bash
set -e

if [ -z "${PREFIX:-}" ] || [ ! -d "$PREFIX" ]; then
    echo "Please start PY-OS from the main Termux app."
    exit 1
fi

cd "$(dirname "$0")"

if ! command -v termux-x11 >/dev/null 2>&1; then
    echo "Termux:X11 is not installed. Run: bash setup.sh"
    exit 1
fi

if [ ! -f pyos.py ]; then
    echo "Could not find pyos.py in this folder."
    exit 1
fi

# Start the X11 display if it is not already running.
if ! pgrep -x termux-x11 >/dev/null 2>&1; then
    termux-x11 :0 >/dev/null 2>&1 &
    sleep 2
fi

export DISPLAY=:0
exec python pyos.py
