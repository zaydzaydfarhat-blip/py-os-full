#!/data/data/com.termux/files/usr/bin/bash

set -Ee

cd "$(dirname "$0")"

export DISPLAY=:0

if ! command -v termux-x11 >/dev/null 2>&1; then
    echo "Install termux-x11-nightly first."
    exit 1
fi

X11_PID=""
GUI_PID=""
STARTED_X11=0

cleanup() {
    trap - EXIT INT TERM TSTP

    if [ -n "$GUI_PID" ]; then
        kill "$GUI_PID" 2>/dev/null || true
        wait "$GUI_PID" 2>/dev/null || true
    fi

    if [ "$STARTED_X11" -eq 1 ] && [ -n "$X11_PID" ]; then
        kill "$X11_PID" 2>/dev/null || true
        wait "$X11_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 148' TSTP

if ! xdpyinfo -display :0 >/dev/null 2>&1; then
    echo "Starting Termux:X11 on display :0..."
    termux-x11 :0 &
    X11_PID=$!
    STARTED_X11=1

    am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1 || true

    echo "Waiting for X11..."

    READY=0
    for i in $(seq 1 60); do
        if xdpyinfo -display :0 >/dev/null 2>&1; then
            READY=1
            break
        fi
        sleep 1
    done

    if [ "$READY" -ne 1 ]; then
        echo "ERROR: Termux:X11 did not become ready."
        exit 1
    fi
fi

echo "X11 is ready!"
echo "Starting PY-OS desktop..."

python pyos.py &
GUI_PID=$!
wait "$GUI_PID"
