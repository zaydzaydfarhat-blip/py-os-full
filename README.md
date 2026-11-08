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

For the graphical desktop, install and open the **Termux:X11 Android app**. Then return to Termux.

## Commands

| Command | Action |
| --- | --- |
| `py-os` | Start the arrow-key terminal interface |
| `py-os-update` | Update the Cli project |
| `py-os-gui` | Start the Tkinter graphical desktop |
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
- The desktop requires Termux:X11. The CLI interface runs in a terminal.
- The optional BusyBox terminal simulator in the TUI uses BusyBox if installed.

## Credits

**Made by ChatGPT · Idea by Zayd**
