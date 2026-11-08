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

DISPLAY_SOCKET="${TMPDIR:-$PREFIX/tmp}/.X11-unix/X0"
X11_PID=""
STARTED_X11=0

cleanup() {
    status=$?
    trap - EXIT INT TERM

    # Never stop a server that was already running before PY-OS started.
    if [ "$STARTED_X11" -eq 1 ] && [ -n "$X11_PID" ]; then
        kill "$X11_PID" 2>/dev/null || true
        wait "$X11_PID" 2>/dev/null || true
    fi

    exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [ ! -S "$DISPLAY_SOCKET" ]; then
    echo "Starting Termux:X11 on display :0..."
    termux-x11 :0 &
    X11_PID=$!
    STARTED_X11=1

    count=0
    while [ "$count" -lt 50 ] && [ ! -S "$DISPLAY_SOCKET" ]; do
        sleep 0.2
        count=$((count + 1))
    done

    if [ ! -S "$DISPLAY_SOCKET" ]; then
        echo "Termux:X11 did not create the display socket:"
        echo "$DISPLAY_SOCKET"
        echo "Open the Termux:X11 Android app and try again."
        exit 1
    fi
fi

# Bring the Termux:X11 Android activity to the foreground when available.
if command -v am >/dev/null 2>&1; then
    am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1 || true
fi

export DISPLAY=:0
echo "Starting PY-OS desktop..."
python pyos.py
