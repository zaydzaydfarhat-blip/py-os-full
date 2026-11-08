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

For the graphical desktop, install the **Termux:X11 Android app** and run `bash setup.sh` from the main Termux app. Setup installs `termux-x11-nightly`, `xorg-xdpyinfo`, Python, and Tkinter. Run `py-os-gui`: it reuses display `:0` if already running, otherwise starts Termux:X11, opens its Android activity, and launches the original PY-OS desktop. **No Openbox, XFCE, or other desktop environment is required.**

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
- Welcome, Calculator, Notes, System Info, and Games apps.
- Games includes Chess (two-player with legal moves), Snake, Tic-Tac-Toe, 2048, Minesweeper, and Pong.
- The Games list scrolls when the window is too small to show every game.
- In any game, press `R` or choose **Restart** to start over; press `Q` or choose **Quit** to close that game.
- Games run locally in PY-OS windows; no browser or internet connection is needed after setup.
- App windows open centered on the screen.
- Move windows by dragging their title bars.
- Resize windows using the bottom-right corner.
- Minimize, maximize/restore, and close controls.
- Taskbar buttons let you hide and restore app windows.
- Notes are saved locally at `~/.local/share/py-os-gui/notes.json`.

The CLI and GUI are separate programs, but they are maintained and updated together in this repository.

## XFCE window test

A small test script opens multiple XFCE Terminal windows so you can check how your XFCE desktop handles separate windows:

```bash
bash tests/xfce-window-test.sh
```

You can choose the number of windows (1–12); the default is 8:

```bash
bash tests/xfce-window-test.sh 10
```

This test requires an active graphical session and `xfce4-terminal`. Close the test windows normally when finished.

For a continuous test, run:

```bash
bash tests/xfce-window-test-loop.sh
```

It opens another window every 2 seconds, but never tracks more than 12 open test windows at once. Close windows to let it continue opening replacements. Press **Ctrl+C** in the launching terminal to stop the loop; already-open test windows stay open.

## Notes

- Run `bash setup.sh` from the cloned project folder in the main Termux app.
- If you move the project folder, run `bash setup.sh` again to refresh the command paths.
- The GUI requires the Termux:X11 Android app. The `py-os-gui` launcher attempts to open its activity automatically.
- Use the desktop's **Leave** button, Ctrl+C, or Ctrl+Z to exit. The launcher cleans up the GUI and only stops the X11 server process it started; if an X11 server was already running, PY-OS leaves it running.
- The optional BusyBox terminal simulator in the CLI uses BusyBox if installed.

## Credits

**Made by ChatGPT · Idea by Zayd**
