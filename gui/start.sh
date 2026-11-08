#!/data/data/com.termux/files/usr/bin/bash
set -e

if [ -z "${PREFIX:-}" ] || [ ! -d "$PREFIX" ]; then
    echo "Please start PY-OS from the main Termux app, not inside PRoot."
    exit 1
fi

cd "$(dirname "$0")"

if ! command -v termux-x11 >/dev/null 2>&1; then
    echo "Termux:X11 is not installed. Run the PY-OS setup script first."
    exit 1
fi

if [ ! -f pyos.py ]; then
    echo "Could not find pyos.py in this folder."
    exit 1
fi

X11_PID=""
GUI_PID=""

cleanup() {
    status=$?
    trap - EXIT INT TERM HUP TSTP

    # Stop only the GUI child started by this launcher.
    if [ -n "$GUI_PID" ] && kill -0 "$GUI_PID" 2>/dev/null; then
        kill -TERM "$GUI_PID" 2>/dev/null || true
        wait "$GUI_PID" 2>/dev/null || true
    fi

    # Stop only the X11 server process started by this launcher.
    # If a server was already running before PY-OS started, leave it alone.
    if [ -n "$X11_PID" ] && kill -0 "$X11_PID" 2>/dev/null; then
        kill -TERM "$X11_PID" 2>/dev/null || true
        wait "$X11_PID" 2>/dev/null || true
    fi

    exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
# Ctrl+Z normally suspends a foreground job. For PY-OS, treat it as
# a request to leave so the desktop and its X11 server are cleaned up.
trap 'exit 148' TSTP

# Reuse an existing :0 server, otherwise start one and remember its PID.
if pgrep -x termux-x11 >/dev/null 2>&1; then
    echo "Reusing the existing Termux:X11 server on display :0."
else
    echo "Starting Termux:X11 on display :0..."
    termux-x11 :0 >/dev/null 2>&1 &
    X11_PID=$!
    sleep 2
    if ! kill -0 "$X11_PID" 2>/dev/null; then
        echo "Termux:X11 did not stay running. Open the Termux:X11 Android app and try again."
        exit 1
    fi
fi

export DISPLAY=:0
echo "Starting PY-OS desktop. Press Ctrl+C, Ctrl+Z, or use Leave to exit."

python pyos.py &
GUI_PID=$!
set +e
wait "$GUI_PID"
GUI_STATUS=$?
set -e
GUI_PID=""
exit "$GUI_STATUS"
