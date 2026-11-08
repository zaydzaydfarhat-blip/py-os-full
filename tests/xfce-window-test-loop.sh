#!/usr/bin/env bash
# Continuous XFCE window test, with a strict limit on simultaneous windows.
set -u

MAX_OPEN=12
INTERVAL=2
pids=()
next=1

if ! command -v xfce4-terminal >/dev/null 2>&1; then
    echo "Error: xfce4-terminal is not installed."
    echo "Install it with: sudo apt install xfce4-terminal"
    exit 1
fi

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
    echo "Error: no graphical display is available. Start XFCE first."
    exit 1
fi

cleanup() {
    echo
    echo "Stopping the window test. Test windows already opened will stay open."
    exit 0
}
trap cleanup INT TERM

echo "Continuous XFCE window test started."
echo "Opens a new window every $INTERVAL seconds, with at most $MAX_OPEN open."
echo "Press Ctrl+C to stop opening more windows."

while true; do
    # Remove terminal processes whose windows have been closed.
    alive=()
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            alive+=("$pid")
        fi
    done
    pids=("${alive[@]}")

    if (( ${#pids[@]} < MAX_OPEN )); then
        title="XFCE Continuous Test #$next"
        xfce4-terminal --disable-server --title="$title" --hold \
            --command="printf 'Continuous XFCE window test\\nWindow number: $next\\n\\nClose this window to allow another one to open.\\n'" \
            >/dev/null 2>&1 &
        pids+=("$!")
        echo "Opened window #$next (${#pids[@]}/$MAX_OPEN currently tracked)."
        next=$((next + 1))
    fi

    sleep "$INTERVAL"
done
