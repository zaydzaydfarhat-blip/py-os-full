#!/usr/bin/env bash
# Open a small, controlled batch of XFCE Terminal windows for desktop testing.
set -u

DEFAULT_COUNT=8
MAX_COUNT=12
COUNT="${1:-$DEFAULT_COUNT}"

if ! command -v xfce4-terminal >/dev/null 2>&1; then
    echo "Error: xfce4-terminal is not installed."
    echo "Install it with: sudo apt install xfce4-terminal"
    exit 1
fi

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
    echo "Error: no graphical display is available."
    echo "Start your XFCE desktop first, then run this script again."
    exit 1
fi

if [[ ! "$COUNT" =~ ^[0-9]+$ ]] || (( COUNT < 1 || COUNT > MAX_COUNT )); then
    echo "Usage: $0 [number-of-windows]"
    echo "Choose a number from 1 to $MAX_COUNT (default: $DEFAULT_COUNT)."
    exit 2
fi

echo "Opening $COUNT XFCE test windows..."
for ((i = 1; i <= COUNT; i++)); do
    title="XFCE Window Test $i/$COUNT"
    xfce4-terminal --disable-server --title="$title" --hold \
        --command="printf 'PY-OS XFCE window test\\nWindow: $i of $COUNT\\n\\nClose this window when finished.\\n'" \
        >/dev/null 2>&1 &
    sleep 0.25
done

echo "Done. Close the test windows normally when you're finished."
