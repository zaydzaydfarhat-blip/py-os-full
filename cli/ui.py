#!/usr/bin/env python3
"""Compact arrow-key terminal interface for PY-OS. Uses only Python's standard library."""

from __future__ import annotations

import curses
import datetime as dt
import getpass
import os
import platform
import shutil
import shlex
import signal
import sys
from pathlib import Path

from shell import HOME, VERSION, calculate

MENU = ["Home", "Calculator", "Fastfetch", "Files", "Mini games", "Terminal", "Exit"]
KEYS = ["↑/↓ move", "ENTER select", "Q go back", "ESC exit"]


def safe_add(win, y: int, x: int, text: str, attr: int = 0) -> None:
    height, width = win.getmaxyx()
    if 0 <= y < height and x < width:
        try:
            win.addnstr(y, max(0, x), str(text), max(0, width - max(0, x) - 1), attr)
        except curses.error:
            pass


def setup_colors() -> None:
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)


def frame(stdscr, title: str, subtitle: str = "") -> tuple[int, int]:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    safe_add(stdscr, 0, 2, f" PY-OS {VERSION} ")
    safe_add(stdscr, 0, max(2, w - len(title) - 4), title)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    safe_add(stdscr, 1, 2, "─" * max(1, w - 4))
    if subtitle:
        safe_add(stdscr, h - 2, 2, subtitle, curses.A_DIM)
    safe_add(stdscr, h - 1, 2, "PY-OS • terminal interface", curses.A_DIM)
    return h, w


def message(stdscr, title: str, lines: list[str]) -> None:
    while True:
        h, w = frame(stdscr, title, "Press any key to return")
        for i, line in enumerate(lines[: max(0, h - 5)]):
            safe_add(stdscr, 3 + i, 3, line)
        stdscr.refresh()
        stdscr.getch()
        return


def fastfetch_lines() -> list[str]:
    try:
        disk = shutil.disk_usage(HOME)
        disk_text = f"{disk.used / 1024**3:.1f} / {disk.total / 1024**3:.1f} GiB"
    except OSError:
        disk_text = "Unavailable"
    return [
        "  ____  __   __       ___  ____",
        " |  _ \\ \\ \\ / /      / _ \\/ ___|",
        " | |_) | \\ V / _____| | | \\___ \\",
        " |  __/   | | |_____| |_| |___) |",
        " |_|      |_|        \\___/|____/",
        "          PYTHON TERMINAL OS",
        "",
        f"{getpass.getuser()}@{platform.node() or 'device'}",
        "─" * 30,
        f"OS          PY-OS {VERSION}",
        f"Host        {platform.system()} {platform.release()}",
        f"Architecture {platform.machine()}",
        f"Python      {platform.python_version()}",
        f"Terminal    {os.environ.get('TERM', 'unknown')}",
        f"Workspace   {HOME}",
        f"Disk        {disk_text}",
        f"Date        {dt.datetime.now().astimezone():%Y-%m-%d %H:%M:%S}",
    ]


def home_screen(stdscr) -> str:
    selected = 0
    while True:
        h, w = frame(stdscr, "HOME", "↑/↓ select • ENTER open • Q quit")
        safe_add(stdscr, 3, 4, "Welcome to your terminal.", curses.A_BOLD)
        safe_add(stdscr, 4, 4, "A small TUI — not a full desktop GUI.")
        start_y = 6
        for i, item in enumerate(MENU):
            attr = curses.color_pair(2) | curses.A_BOLD if i == selected else 0
            safe_add(stdscr, start_y + i, 5, f" {('›' if i == selected else ' ')} {item} ", attr)
        safe_add(stdscr, 6, min(w - 28, 36), "Quick tips", curses.A_BOLD)
        safe_add(stdscr, 8, min(w - 28, 36), "Use arrow keys")
        safe_add(stdscr, 9, min(w - 28, 36), "to move around.")
        safe_add(stdscr, 10, min(w - 28, 36), "Open Calculator")
        safe_add(stdscr, 11, min(w - 28, 36), "for a keypad.")
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            selected = (selected - 1) % len(MENU)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = (selected + 1) % len(MENU)
        elif key in (10, 13, curses.KEY_ENTER):
            return MENU[selected]
        elif key in (ord("q"), ord("Q"), 27):
            return "Exit"


def calculator(stdscr) -> None:
    # A compact, responsive 4-column block keypad.
    buttons = ["7", "8", "9", "/", "4", "5", "6", "*",
               "1", "2", "3", "-", "0", ".", "C", "+",
               "(", ")", "⌫", "="]
    cols = 4
    selected = 0
    expression = ""
    result = "Choose a block • ENTER"
    while True:
        h, w = frame(stdscr, "CALCULATOR", "Arrows move • ENTER select • Q back")
        inner_w = max(1, w - 6)
        safe_add(stdscr, 2, 3, "CALCULATOR", curses.A_BOLD)
        # Display panel adapts to narrow terminals.
        display_width = min(inner_w, 48)
        display_x = max(2, (w - display_width) // 2)
        safe_add(stdscr, 4, display_x, "┌" + "─" * max(1, display_width - 2) + "┐", curses.color_pair(1))
        shown = expression[-max(1, display_width - 6):] or "0"
        safe_add(stdscr, 5, display_x, "│ " + shown[:max(1, display_width - 4)].ljust(max(1, display_width - 4)) + " │", curses.color_pair(3) | curses.A_BOLD)
        safe_add(stdscr, 6, display_x, "└" + "─" * max(1, display_width - 2) + "┘", curses.color_pair(1))
        safe_add(stdscr, 7, 3, result[:max(1, inner_w)])
        # Four equally spaced cells fill the available width.
        gap = 1
        cell_w = max(3, min(10, (inner_w - (cols - 1) * gap) // cols))
        total_w = cols * cell_w + (cols - 1) * gap
        start_x = max(2, (w - total_w) // 2)
        start_y = 9
        row_h = 2
        for i, label in enumerate(buttons):
            row, col = divmod(i, cols)
            y = start_y + row * row_h
            x = start_x + col * (cell_w + gap)
            if y >= h - 3:
                continue
            text = ("[" + label.center(max(1, cell_w - 2)) + "]")[:cell_w]
            attr = curses.color_pair(2) | curses.A_BOLD if i == selected else curses.color_pair(1)
            safe_add(stdscr, y, x, text.ljust(cell_w), attr)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return
        if key == curses.KEY_UP:
            selected = (selected - cols) % len(buttons)
        elif key == curses.KEY_DOWN:
            selected = (selected + cols) % len(buttons)
        elif key == curses.KEY_LEFT:
            selected = (selected - 1) % len(buttons)
        elif key == curses.KEY_RIGHT:
            selected = (selected + 1) % len(buttons)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            expression = expression[:-1]
        elif key in (10, 13, curses.KEY_ENTER):
            value = buttons[selected]
            if value == "C":
                expression, result = "", "Cleared"
            elif value == "⌫":
                expression = expression[:-1]
                result = "Deleted last character"
            elif value == "=":
                try:
                    answer = calculate(expression)
                    expression = str(answer)
                    result = "Result"
                except Exception as error:
                    result = f"Error: {error}"
            else:
                expression += value
                result = "Ready"
        elif 32 <= key <= 126:
            char = chr(key)
            if char in "0123456789.+-*/()":
                expression += char
                result = "Ready"


def files_screen(stdscr) -> None:
    folder = HOME
    offset = 0
    selected = 0
    while True:
        try:
            entries = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except OSError:
            entries = []
        h, w = frame(stdscr, "FILES", "↑/↓ select • ENTER open folder • BACKSPACE up • Q back")
        safe_add(stdscr, 3, 3, str(folder), curses.A_BOLD)
        visible = max(1, h - 7)
        selected = min(selected, max(0, len(entries) - 1))
        if selected < offset:
            offset = selected
        if selected >= offset + visible:
            offset = selected - visible + 1
        for row, entry in enumerate(entries[offset:offset + visible]):
            i = offset + row
            label = entry.name + ("/" if entry.is_dir() else "")
            attr = curses.color_pair(2) if i == selected else 0
            safe_add(stdscr, 5 + row, 5, label, attr)
        if not entries:
            safe_add(stdscr, 5, 5, "(empty folder)")
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return
        if key == curses.KEY_UP and entries:
            selected = (selected - 1) % len(entries)
        elif key == curses.KEY_DOWN and entries:
            selected = (selected + 1) % len(entries)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if folder != HOME:
                folder = folder.parent
                selected = offset = 0
        elif key in (10, 13, curses.KEY_ENTER) and entries:
            target = entries[selected]
            if target.is_dir():
                folder = target
                selected = offset = 0
            else:
                try:
                    data = target.read_text(encoding="utf-8").splitlines()
                    message(stdscr, target.name, data[:100] or ["(empty file)"])
                except (OSError, UnicodeError):
                    message(stdscr, "FILE", ["This file cannot be previewed as text."])


def terminal_screen(stdscr) -> None:
    """A Debian-looking BusyBox terminal simulator inside the PY-OS TUI."""
    history: list[str] = ["PY-OS BusyBox Terminal", "Type help to list available commands."]
    command_history: list[str] = []
    history_index = 0
    current = ""
    cwd = HOME
    busybox = shutil.which("busybox")
    safe_applets = {
        "ls", "cat", "echo", "date", "whoami", "uname", "id", "head",
        "tail", "wc", "grep", "sort", "cut", "tr", "basename",
        "dirname", "printf", "test", "true", "false",
    }
    applets: set[str] = set()
    if busybox:
        try:
            result = __import__("subprocess").run(
                [busybox, "--list"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                applets = set(result.stdout.split()) & safe_applets
        except (OSError, __import__("subprocess").SubprocessError):
            applets = set()

    def add(text: str) -> None:
        history.extend(str(text).rstrip("\n").splitlines() or [""])

    def resolve_path(value: str) -> Path:
        target = (cwd / os.path.expanduser(value)).resolve()
        root = HOME.resolve()
        if target != root and root not in target.parents:
            raise ValueError("Path is outside the PY-OS workspace.")
        return target

    while True:
        h, w = frame(stdscr, "BUSYBOX TERMINAL", "ENTER run • ↑/↓ history • Q back (when input is empty)")
        visible = max(1, h - 8)
        for i, line in enumerate(history[-visible:]):
            safe_add(stdscr, 3 + i, 3, line)
        try:
            shown = "~" + str(cwd.relative_to(HOME)) if cwd != HOME else "~"
        except ValueError:
            shown = str(cwd)
        prompt = f"debian:{shown}$ "
        safe_add(stdscr, h - 4, 3, (prompt + current)[-(w - 6):], curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord("q"), ord("Q"), 27) and not current:
            return
        if key in (10, 13, curses.KEY_ENTER):
            line = current.strip()
            current = ""
            if not line:
                continue
            command_history.append(line)
            history_index = len(command_history)
            add(prompt + line)
            try:
                bits = shlex.split(line)
                if not bits:
                    continue
                name, args = bits[0].lower(), bits[1:]
                if name in ("exit", "quit"):
                    add("Leaving the BusyBox terminal. Press Q to return.")
                elif name == "help":
                    add("Built-ins: help, cd, clear, history, pwd, exit")
                    add("Safe BusyBox applets available on this device:")
                    add("  " + ("  ".join(sorted(applets)) if applets else "BusyBox not found; install it with: pkg install busybox"))
                elif name == "clear":
                    history.clear()
                elif name == "history":
                    for index, item in enumerate(command_history, 1):
                        add(f"{index:4}  {item}")
                elif name == "pwd":
                    add(str(cwd))
                elif name == "cd":
                    target = resolve_path(args[0] if args else str(HOME))
                    if target.is_dir():
                        cwd = target
                    else:
                        add(f"cd: {args[0] if args else target}: No such directory")
                elif name in applets and busybox:
                    import subprocess
                    result = subprocess.run(
                        [busybox, name, *args], cwd=str(cwd),
                        capture_output=True, text=True, timeout=10
                    )
                    if result.stdout:
                        add(result.stdout)
                    if result.stderr:
                        add(result.stderr)
                    if result.returncode:
                        add(f"[exit code {result.returncode}]")
                elif name in safe_applets and not busybox:
                    add("BusyBox is not installed. In main Termux run: pkg install busybox")
                else:
                    add(f"{name}: command not available. Type help.")
            except ValueError as error:
                add(f"Input error: {error}")
            except __import__("subprocess").TimeoutExpired:
                add("Command timed out after 10 seconds.")
            except OSError as error:
                add(f"Command error: {error}")
        elif key == curses.KEY_UP:
            if command_history:
                history_index = max(0, history_index - 1)
                current = command_history[history_index]
        elif key == curses.KEY_DOWN:
            if command_history:
                history_index = min(len(command_history), history_index + 1)
                current = command_history[history_index] if history_index < len(command_history) else ""
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            current = current[:-1]
        elif 32 <= key <= 126 and len(current) < max(1, w - 18):
            current += chr(key)


def games_screen(stdscr) -> None:
    choices = ["Guess the number", "Roll a dice", "Flip a coin", "Back"]
    selected = 0
    import random
    while True:
        h, w = frame(stdscr, "MINI GAMES", "↑/↓ select • ENTER play • Q back")
        for i, label in enumerate(choices):
            safe_add(stdscr, 4 + i * 2, 5, f" {label} ", curses.color_pair(2) if i == selected else 0)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(choices)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(choices)
        elif key in (10, 13, curses.KEY_ENTER):
            if selected == 3:
                return
            if selected == 0:
                answer = random.randint(1, 20)
                message(stdscr, "GUESS", [f"Think of a number from 1 to 20.", f"Your lucky number is {answer}."])
            elif selected == 1:
                message(stdscr, "DICE", [f"You rolled: {random.randint(1, 6)}"])
            else:
                message(stdscr, "COIN", [random.choice(["Heads!", "Tails!"])])


def app(stdscr) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    setup_colors()
    while True:
        choice = home_screen(stdscr)
        if choice == "Exit":
            return
        if choice == "Calculator":
            calculator(stdscr)
        elif choice == "Fastfetch":
            message(stdscr, "FASTFETCH", fastfetch_lines())
        elif choice == "Files":
            files_screen(stdscr)
        elif choice == "Mini games":
            games_screen(stdscr)
        elif choice == "Terminal":
            terminal_screen(stdscr)
        elif choice == "Home":
            message(stdscr, "ABOUT PY-OS", [
                "PY-OS is a compact terminal interface.",
                "Use the arrow keys to navigate menus.",
                "It is not a full desktop environment.",
                "",
                "Press any key to return.",
            ])


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if hasattr(signal, "SIGTSTP"):
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    try:
        curses.wrapper(app)
    except curses.error:
        print("PY-OS needs a real terminal with at least 50 columns and 16 rows.")
        print("Try resizing your terminal, then run: python main.py")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
