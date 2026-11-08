#!/usr/bin/env python3
"""PY-OS launcher: compact arrow-key TUI by default, classic shell optional."""

import sys
import signal


def protect_terminal_shortcuts() -> None:
    """Keep Ctrl+C and Ctrl+Z from stopping or suspending PY-OS."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if hasattr(signal, "SIGTSTP"):
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)


def main() -> None:
    protect_terminal_shortcuts()
    if "--shell" in sys.argv:
        from shell import main as shell_main
        shell_main()
    else:
        try:
            from ui import main as ui_main
            ui_main()
        except ImportError as error:
            print("Could not start the PY-OS terminal interface.")
            print(f"Details: {error}")
            print("Try running: python main.py --shell")

if __name__ == "__main__":
    main()
