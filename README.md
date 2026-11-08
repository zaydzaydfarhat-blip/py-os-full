# PY-OS Full

PY-OS Full combines **PY-OS CLI** and **PY-OS GUI** in one project for Termux. Both programs live in the same GitHub repository, so one `git pull` updates both.

## Install on Termux

Use the main Termux app (not a PRoot shell):

```bash
pkg install git
git clone https://github.com/zaydzaydfarhat-blip/py-os-full
cd py-os-full
bash setup.sh
```

For the graphical desktop, also install the **Termux:X11 Android app**. Then run `py-os-gui` from the main Termux app. The launcher starts the X11 server on display `:0` only when it is not already running.

## Commands

| Command | Action |
| --- | --- |
| `py-os` | Start the arrow-key terminal interface |
| `py-os-update` | Update the combined repository |
| `py-os-gui` | Start the PY-OS graphical desktop |
| `py-os-gui-update` | Update the combined repository |
| `py-os-full-update` | Update the complete PY-OS project |

All three update commands update the same combined repository, including both CLI and GUI. You can also update everything yourself with:

```bash
cd ~/py-os-full
git pull
```

## What's included

- `cli/` — the PY-OS terminal interface and its supporting files.
- `gui/` — the Tkinter desktop, X11 launcher, and web demo files.
- `setup.sh` — installs the required dependencies and the five command launchers into Termux's `$PREFIX/bin`.

### PY-OS GUI desktop

- Desktop wallpaper, app shortcuts, clock, and Start menu.
- Welcome, Calculator, Notes, and System Info apps.
- App windows open centered on the screen.
- Move windows by dragging their title bars.
- Resize windows using the bottom-right corner.
- Minimize, maximize/restore, and close controls.
- Taskbar buttons let you hide and restore app windows.
- Notes are saved locally at `~/.local/share/py-os-gui/notes.json`.

The CLI and GUI are separate programs, but they are maintained and updated together in this repository.

## Notes

- Run `bash setup.sh` from the cloned project folder in the main Termux app.
- If you move the project folder, run `bash setup.sh` again to refresh the command paths.
- The GUI requires the Termux:X11 Android app. Open that app if the desktop does not appear.
- Use the desktop's **Leave** button or Ctrl+C to exit. The launcher only stops the X11 server process it started; if an X11 server was already running, PY-OS leaves it running.
- The optional BusyBox terminal simulator in the CLI uses BusyBox if installed.

## Credits

**Made by ChatGPT · Idea by Zayd**
