# PY-OS Full

PY-OS Full combines the original **PY-OS terminal interface** and **PY-OS GUI desktop** in one Termux project.

## Install on Termux

Use the main Termux app (not a PRoot shell):

```bash
pkg install git
git clone https://github.com/zaydzaydfarhat-blip/py-os-full
cd py-os-full
bash setup.sh
```

For the graphical desktop, install the **Termux:X11 Android app**. Then run `py-os-gui` from the main Termux app; the launcher starts the Termux:X11 server on display `:0` if it is not already running.

## Commands

| Command | Action |
| --- | --- |
| `py-os` | Start the arrow-key terminal interface |
| `py-os-update` | Update the Cli project |
| `py-os-gui` | Start Termux:X11 on display `:0` (if needed), then start the desktop |
| `py-os-gui-update` | Update the Gui project |
| `py-os-full-update` | Update the entire PY-OS Full repository |

All three update commands pull the latest version of the same combined repository.

## What's included

- `cli/` — original terminal launcher, interactive TUI, and classic shell.
- `gui/` — original Tkinter desktop, Termux:X11 start script, and web demo files.
- `setup.sh` — installs dependencies and all five command launchers into Termux's `$PREFIX/bin`.

The terminal interface and desktop remain separate programs; you can run either one.

## Notes

- Run setup from the cloned project folder in the main Termux app.
- If you move the project folder, run `bash setup.sh` again to refresh the command paths.
- The desktop requires the Termux:X11 Android app to be installed. `py-os-gui` starts the X11 server on display `:0` when needed. Use the desktop's **Leave** button, Ctrl+C, or Ctrl+Z to exit; the launcher stops only the X11 server process it started. If an X11 server was already running, PY-OS leaves it running.
- The optional BusyBox terminal simulator in the TUI uses BusyBox if installed.

## Credits

**Made by ChatGPT · Idea by Zayd**
