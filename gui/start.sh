#!/data/data/com.termux/files/usr/bin/bash
set -e

if [ -z "${PREFIX:-}" ] || [ ! -d "$PREFIX" ]; then
    echo "Please start PY-OS from the main Termux app, not inside PRoot."
    exit 1
fi

cd "$(dirname "$0")"

if ! command -v termux-x11 >/dev/null 2>&1; then
    echo "Termux:X11 companion package is missing."
    echo "Install it in main Termux with: pkg install x11-repo termux-x11-nightly"
    exit 1
fi

if [ ! -f pyos.py ]; then
    echo "Could not find pyos.py in this folder."
    exit 1
fi

X11_PID=""
STARTED_X11=0

cleanup() {
    status=$?
    trap - EXIT INT TERM

    # Only stop the X11 process if this launcher started it.
    if [ "$STARTED_X11" -eq 1 ] && [ -n "$X11_PID" ]; then
        kill "$X11_PID" 2>/dev/null || true
        wait "$X11_PID" 2>/dev/null || true
    fi

    exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if pgrep -x termux-x11 >/dev/null 2>&1; then
    echo "Termux:X11 is already running; reusing display :0."
else
    echo "Starting Termux:X11 on display :0..."
    termux-x11 :0 &
    X11_PID=$!
    STARTED_X11=1
fi

export DISPLAY=:0
echo "Waiting briefly for Termux:X11..."
sleep 2

echo "Starting PY-OS desktop..."
python pyos.py
