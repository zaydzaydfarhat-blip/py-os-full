#!/usr/bin/env python3
"""PY-OS: a colorful, fastfetch-inspired terminal environment."""

from __future__ import annotations

import ast
import datetime as dt
import getpass
import os
import platform
import random
try:
    import readline  # Enables Up/Down command history in interactive terminals.
except ImportError:
    readline = None
import shlex
import signal
import shutil
import sys
from pathlib import Path

VERSION = "2.0.0"
HOME = Path.home() / "py-os-home"
HOME.mkdir(parents=True, exist_ok=True)

LOGO = [
    "  ____  __   __       ___  ____ ",
    " |  _ \\ \\ \\ / /      / _ \\/ ___|",
    " | |_) | \\ V / _____| | | \\___ \\",
    " |  __/   | | |_____| |_| |___) |",
    " |_|      |_|        \\___/|____/",
    "          PYTHON TERMINAL OS",
]
COLORS = {
    "default": "",
    "green": "\033[32m",
    "blue": "\033[94m",
    "amber": "\033[33m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "red": "\033[31m",
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
theme = "cyan"
current_dir = HOME
history: list[str] = []

HELP = {
    "help": "Show all commands",
    "fastfetch": "Show the PY-OS ASCII logo and system information",
    "neofetch / fetch": "Aliases for fastfetch",
    "about": "About this project",
    "clear": "Clear the terminal",
    "reboot": "Show the startup screen",
    "exit": "Exit PY-OS",
    "whoami": "Show the current username",
    "date": "Show date and time",
    "sysinfo": "Show detailed system information",
    "pwd": "Print the current workspace folder",
    "ls [--all]": "List files in the current folder",
    "tree": "Show a small folder tree",
    "cd FOLDER": "Change folder (cd with no argument returns home)",
    "mkdir NAME": "Create a folder",
    "touch FILE": "Create an empty file",
    "cat FILE": "Display a text file",
    "write FILE": "Write a text file; finish with .save",
    "rm FILE": "Delete a file; use rm -r or rm -rf for folders",
    "rmdir FOLDER": "Delete an empty folder",
    "calc EXPRESSION": "Calculate basic arithmetic",
    "echo TEXT": "Print text",
    "theme NAME": "Set theme: green, blue, amber, purple, cyan, red, default",
    "history": "Show commands entered this session",
    "date": "Show current date and time",
    "guess": "Play the number guessing game",
    "roll": "Roll a six-sided dice",
    "coin": "Flip a coin",
}

def paint(text: str, *, bold: bool = False) -> str:
    color = COLORS[theme]
    return f"{BOLD if bold else ''}{color}{text}{RESET}" if color or bold else text

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def safe_path(name: str) -> Path:
    """Keep PY-OS file commands inside the dedicated workspace."""
    target = (current_dir / name).resolve()
    root = HOME.resolve()
    if target != root and root not in target.parents:
        raise ValueError("File access is restricted to your py-os-home workspace.")
    return target

def calculate(expression: str) -> int | float:
    """Evaluate a restricted arithmetic expression."""
    tree = ast.parse(expression, mode="eval")
    allowed = (
        ast.Expression, ast.Constant, ast.BinOp, ast.UnaryOp,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
        ast.Pow, ast.USub, ast.UAdd, ast.Load,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError("Only basic arithmetic is supported.")
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ValueError("Only numbers are allowed.")
            if abs(node.value) > 1_000_000:
                raise ValueError("Input number is too large.")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            if not isinstance(node.right, ast.Constant) or not isinstance(node.right.value, (int, float)):
                raise ValueError("Use a numeric exponent.")
            if abs(node.right.value) > 8:
                raise ValueError("Power is limited to 8.")
    result = eval(compile(tree, "<py-os-calc>", "eval"), {"__builtins__": {}}, {})
    if isinstance(result, complex) or abs(result) > 10**100:
        raise ValueError("Result is too large.")
    return result

def disk_usage(path: Path) -> str:
    try:
        usage = shutil.disk_usage(path)
        total = usage.total
        used = usage.used
        percent = (used / total * 100) if total else 0
        return f"{used / (1024**3):.1f} GiB / {total / (1024**3):.1f} GiB ({percent:.0f}% used)"
    except OSError:
        return "Unavailable"

def fastfetch() -> None:
    """Display a compact Fastfetch-inspired system summary."""
    user = getpass.getuser()
    host = platform.node() or "unknown"
    os_name = platform.system() or "Unknown"
    release = platform.release() or "Unknown"
    shell = os.environ.get("SHELL", "Python command prompt")
    terminal = os.environ.get("TERM", "unknown")
    rows = [
        f"{user}@{host}",
        "─" * max(12, len(user) + len(host) + 1),
        f"{'OS':<12} PY-OS {VERSION} / {os_name} {release}",
        f"{'Host':<12} {platform.machine()}",
        f"{'Kernel':<12} {platform.system()} {platform.release()}",
        f"{'Python':<12} {platform.python_version()}",
        f"{'Shell':<12} {Path(shell).name if shell != 'Python command prompt' else shell}",
        f"{'Terminal':<12} {terminal}",
        f"{'Resolution':<12} {os.environ.get('COLUMNS', 'unknown')} columns",
        f"{'Workspace':<12} {HOME}",
        f"{'Disk':<12} {disk_usage(HOME)}",
        f"{'Date':<12} {dt.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "● ● ● ● ● ●",
    ]
    logo = [paint(line, bold=True) for line in LOGO]
    print()
    for index in range(max(len(logo), len(rows))):
        left = logo[index] if index < len(logo) else " " * 34
        right = rows[index] if index < len(rows) else ""
        print(f"  {left:<42} {paint(right)}")
    print()

def show_sysinfo() -> None:
    print(f"PY-OS version : {VERSION}")
    print(f"User          : {getpass.getuser()}")
    print(f"Platform      : {platform.platform()}")
    print(f"Python        : {platform.python_version()}")
    print(f"Executable    : {sys.executable}")
    print(f"Workspace     : {HOME}")
    print(f"Disk          : {disk_usage(HOME)}")

def show_tree(folder: Path, prefix: str = "", depth: int = 0) -> None:
    if depth >= 3:
        return
    try:
        entries = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError as error:
        print(prefix + str(error))
        return
    for index, entry in enumerate(entries):
        last = index == len(entries) - 1
        print(prefix + ("└── " if last else "├── ") + entry.name + ("/" if entry.is_dir() else ""))
        if entry.is_dir():
            show_tree(entry, prefix + ("    " if last else "│   "), depth + 1)

def boot() -> None:
    clear_screen()
    print(paint("\n".join(LOGO), bold=True))
    print(paint(f"  Version {VERSION}  •  Python {platform.python_version()}  •  {platform.system()}", bold=True))
    print(f"  Workspace: {HOME}")
    print("  Type 'help' for commands or 'fastfetch' for system info.\n")

def command(line: str) -> bool:
    global current_dir, theme
    try:
        parts = shlex.split(line)
    except ValueError as error:
        print(f"Input error: {error}")
        return True
    if not parts:
        return True
    cmd, args = parts[0].lower(), parts[1:]
    try:
        if cmd == "help":
            print(paint("\n  PY-OS COMMAND CENTER", bold=True))
            for name, description in HELP.items():
                print(f"  {paint(name, bold=True):<29} {description}")
            print()
        elif cmd in ("fastfetch", "fetch", "neofetch"):
            fastfetch()
        elif cmd == "about":
            print(f"PY-OS {VERSION}: a Python-powered terminal playground.")
            print("Inspired by classic command-line systems and Fastfetch.")
            print("This runs inside your normal OS; it is not a bootable operating system.")
        elif cmd == "clear":
            clear_screen()
        elif cmd == "reboot":
            boot()
        elif cmd == "exit":
            print("Shutting down PY-OS. Bye!")
            return False
        elif cmd == "whoami":
            print(getpass.getuser())
        elif cmd == "date":
            print(dt.datetime.now().astimezone().strftime("%A, %d %B %Y  %H:%M:%S %Z"))
        elif cmd == "sysinfo":
            show_sysinfo()
        elif cmd == "echo":
            print(" ".join(args))
        elif cmd == "calc":
            print(calculate(" ".join(args)) if args else "Usage: calc 12 * (4 + 2)")
        elif cmd == "pwd":
            print(current_dir)
        elif cmd == "ls":
            show_hidden = "--all" in args or "-a" in args
            entries = sorted(current_dir.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            entries = [p for p in entries if show_hidden or not p.name.startswith(".")]
            if not entries:
                print("  (empty folder)")
            for entry in entries:
                marker = "/" if entry.is_dir() else ""
                print(f"  {paint(entry.name + marker, bold=entry.is_dir())}")
        elif cmd == "tree":
            print(current_dir.name + "/")
            show_tree(current_dir)
        elif cmd == "cd":
            target = safe_path(args[0]) if args else HOME
            if not target.exists() or not target.is_dir():
                print("Folder not found.")
            else:
                current_dir = target
        elif cmd == "mkdir":
            if not args:
                print("Usage: mkdir FOLDER")
            else:
                safe_path(args[0]).mkdir(parents=True, exist_ok=True)
                print("Folder created.")
        elif cmd == "touch":
            if not args:
                print("Usage: touch FILE")
            else:
                safe_path(args[0]).touch(exist_ok=True)
                print("File created.")
        elif cmd == "cat":
            if not args:
                print("Usage: cat FILE")
            else:
                target = safe_path(args[0])
                if not target.is_file():
                    print("File not found.")
                else:
                    print(target.read_text(encoding="utf-8"))
        elif cmd == "write":
            if not args:
                print("Usage: write FILE")
            else:
                target = safe_path(args[0])
                print("Type your text. Enter .save on a line by itself to save.")
                lines = []
                while True:
                    text = input("  ... ")
                    if text == ".save":
                        break
                    lines.append(text)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
                print("Saved.")
        elif cmd == "rmdir":
            if not args:
                print("Usage: rmdir FOLDER")
            else:
                for name in args:
                    target = safe_path(name)
                    if not target.exists():
                        print(f"rmdir: {name}: folder not found")
                    elif not target.is_dir():
                        print(f"rmdir: {name}: not a folder")
                    elif target == HOME or target == current_dir or current_dir in target.parents:
                        print(f"rmdir: {name}: refusing to remove the workspace or a folder containing your current location")
                    else:
                        try:
                            target.rmdir()
                            print(f"Removed empty folder: {name}")
                        except OSError as error:
                            if isinstance(error, OSError) and getattr(error, "errno", None) in (39, 66):
                                print(f"rmdir: {name}: folder is not empty")
                            else:
                                print(f"rmdir: {name}: {error}")
        elif cmd == "rm":
            recursive = False
            force = False
            names = []
            options_done = False
            for item in args:
                if not options_done and item == "--":
                    options_done = True
                elif not options_done and item.startswith("-") and item != "-":
                    if item in ("--recursive", "--force"):
                        recursive = recursive or item == "--recursive"
                        force = force or item == "--force"
                    elif item.startswith("--"):
                        print(f"rm: unknown option: {item}")
                        return True
                    else:
                        for flag in item[1:]:
                            if flag == "r":
                                recursive = True
                            elif flag == "f":
                                force = True
                            else:
                                print(f"rm: invalid option -- '{flag}'")
                                return True
                else:
                    names.append(item)
            if not names:
                print("Usage: rm [-r] [-f] FILE_OR_FOLDER")
                print("       rm -rf FOLDER")
            else:
                for name in names:
                    try:
                        target = safe_path(name)
                        if not target.exists() and not target.is_symlink():
                            if not force:
                                print(f"rm: {name}: not found")
                            continue
                        if target.is_dir() and not target.is_symlink():
                            if not recursive:
                                print(f"rm: {name}: is a folder (use rm -r or rm -rf)")
                            elif target == HOME or target == current_dir or current_dir in target.parents:
                                print(f"rm: {name}: refusing to remove the workspace or a folder containing your current location")
                            else:
                                shutil.rmtree(target)
                                print(f"Removed folder: {name}")
                        else:
                            target.unlink()
                            print(f"Removed: {name}")
                    except (OSError, ValueError) as error:
                        print(f"rm: {name}: {error}")
        elif cmd == "theme":
            if len(args) != 1 or args[0].lower() not in COLORS:
                print("Themes: " + ", ".join(COLORS))
            else:
                theme = args[0].lower()
                print(f"Theme changed to {theme}.")
        elif cmd == "history":
            if not history:
                print("No commands yet.")
            for index, item in enumerate(history, 1):
                print(f"  {index:>3}  {item}")
        elif cmd == "guess":
            answer = random.randint(1, 50)
            print("Guess a number from 1 to 50. You have 6 tries!")
            for attempt in range(1, 7):
                value = input(f"  Try {attempt}/6: ").strip()
                if not value.isdigit():
                    print("  Enter a whole number.")
                    continue
                number = int(value)
                if number == answer:
                    print("  Correct! You won!")
                    break
                print("  Too low!" if number < answer else "  Too high!")
            else:
                print(f"  The number was {answer}.")
        elif cmd == "roll":
            print(f"🎲 You rolled a {random.randint(1, 6)}")
        elif cmd == "coin":
            print("🪙 " + random.choice(("Heads!", "Tails!")))
        else:
            print(f"Unknown command: {cmd}. Type 'help'.")
    except (OSError, ValueError, SyntaxError, ZeroDivisionError, OverflowError) as error:
        print(f"Error: {error}")
    return True

def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if hasattr(signal, "SIGTSTP"):
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    boot()
    print(f"Welcome to PY-OS, {getpass.getuser()}!")
    print("Tip: run fastfetch to see your system summary.\n")
    while True:
        try:
            prompt = paint(f" {getpass.getuser()}@py-os ", bold=True) + paint(f"{current_dir.name} $ ")
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down PY-OS.")
            break
        if line:
            history.append(line)
            if not command(line):
                break

if __name__ == "__main__":
    main()
