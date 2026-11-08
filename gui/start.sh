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

mkdir -p "$HOME/.local/share/py-os-gui"
X11_LOG="$HOME/.local/share/py-os-gui/termux-x11.log"
X11_PID=""
GUI_PID=""
STARTED_X11=0

# Remember existing server PIDs so PY-OS never stops a server it did not start.
BEFORE_PIDS="$(pgrep -x termux-x11 2>/dev/null || true)"

cleanup() {
    status=$?
    trap - EXIT INT TERM HUP TSTP

    if [ -n "$GUI_PID" ] && kill -0 "$GUI_PID" 2>/dev/null; then
        kill -TERM "$GUI_PID" 2>/dev/null || true
        wait "$GUI_PID" 2>/dev/null || true
    fi

    # Stop only newly-created Termux:X11 server processes, not pre-existing ones.
    if [ "$STARTED_X11" -eq 1 ]; then
        AFTER_PIDS="$(pgrep -x termux-x11 2>/dev/null || true)"
        for pid in $AFTER_PIDS; do
            case " $BEFORE_PIDS " in
                *" $pid "*) ;;
                *) kill -TERM "$pid" 2>/dev/null || true ;;
            esac
        done
        if [ -n "$X11_PID" ] && kill -0 "$X11_PID" 2>/dev/null; then
            kill -TERM "$X11_PID" 2>/dev/null || true
        fi
    fi

    exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
# Treat Ctrl+Z as a request to leave, rather than suspending the desktop.
trap 'exit 148' TSTP

# Reuse an existing server; otherwise launch one and wait for its display socket.
if [ -n "$BEFORE_PIDS" ]; then
    echo "Termux:X11 server is already running; reusing display :0."
else
    echo "Starting Termux:X11 on display :0..."
    termux-x11 :0 >"$X11_LOG" 2>&1 &
    X11_PID=$!
    STARTED_X11=1

    SOCKET=""
    for candidate in "${TMPDIR:-$PREFIX/tmp}/.X11-unix/X0" "/tmp/.X11-unix/X0"; do
        count=0
        while [ "$count" -lt 100 ]; do
            if [ -S "$candidate" ] || [ -e "$candidate" ]; then
                SOCKET="$candidate"
                break
            fi
            sleep 0.2
            count=$((count + 1))
        done
        [ -n "$SOCKET" ] && break
    done

    if [ -z "$SOCKET" ]; then
        echo "Termux:X11 did not create the display :0 socket."
        echo "Check that the Termux:X11 Android app is installed and open."
        echo "Startup log: $X11_LOG"
        if [ -s "$X11_LOG" ]; then
            echo "--- Last Termux:X11 messages ---"
            tail -n 20 "$X11_LOG"
        fi
        exit 1
    fi
    echo "Display :0 is ready."
fi

# Bring the Android X11 activity to the front if the standalone app is installed.
if command -v am >/dev/null 2>&1; then
    am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1 || true
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
