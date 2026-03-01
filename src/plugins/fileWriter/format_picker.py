"""
Interactive format selector for FileOutputSink.
Arrow keys to move, Enter to confirm, works on Windows + Unix.
"""

from __future__ import annotations
import sys


# ── ANSI ──────────────────────────────────────────────────────────────────────
R = "\033[0m"
B = "\033[1m"
GOLD = "\033[93m"
CYAN = "\033[96m"
GREEN = "\033[92m"
GRAY = "\033[90m"
DIM = "\033[2m"
CLR = "\033[2K\033[1G"  # clear line + go to col 1
UP = "\033[1A"  # move cursor up 1

MENU_ITEMS = [
    ("html", "HTML", "dark-themed standalone report, opens in browser"),
    ("pdf", "PDF", "multi-page formatted document via ReportLab"),
    ("markdown", "Markdown", "clean .md with tables, great for Git / docs"),
    ("csv", "CSV", "zip of one CSV per section, ready for Excel"),
    ("json", "JSON", "pretty-printed JSON with full metadata"),
]


def _enable_ansi_windows() -> None:
    """Enable VT100 sequences on Windows 10+."""
    if sys.platform == "win32":
        import ctypes

        kernel = ctypes.windll.kernel32
        kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)


def _getch():
    """Read a single keypress, returning a normalised token."""
    if sys.platform == "win32":
        import msvcrt

        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):  # special key prefix
            ch2 = msvcrt.getch()
            return {"H": "UP", "P": "DOWN", "\r": "ENTER", "M": "RIGHT"}.get(
                ch2.decode(errors="ignore"), ""
            )
        return ch.decode(errors="ignore")
    else:
        import tty, termios

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch2 = sys.stdin.read(2)
                return {"[A": "UP", "[B": "DOWN", "[C": "RIGHT"}.get(ch2, "ESC")
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _render_menu(selected: int, title: str = "Select output format") -> None:
    """Print the full menu (called on first draw and after each keypress)."""
    print(f"\n  {B}{GOLD}❯  {title}{R}\n")
    for i, (fmt, label, desc) in enumerate(MENU_ITEMS):
        if i == selected:
            cursor = f"{CYAN}{B}▶{R}"
            row = f"  {cursor}  {CYAN}{B}{label:<12}{R}  {DIM}{GRAY}{desc}{R}"
        else:
            cursor = f"{GRAY} {R}"
            row = f"  {cursor}  {GRAY}{label:<12}  {DIM}{desc}{R}"
        print(row)
    print(f"\n  {DIM}{GRAY}↑ ↓  navigate   Enter  confirm{R}\n")


def _clear_menu(n_lines: int) -> None:
    """Erase the rendered menu from the terminal."""
    for _ in range(n_lines):
        sys.stdout.write(f"{UP}{CLR}")
    sys.stdout.flush()


def pick_format() -> str:
    """
    Show an interactive arrow-key menu and return the chosen format string.
    Falls back to a plain numbered prompt if the terminal is not interactive.
    """
    _enable_ansi_windows()

    # Non-interactive fallback (piped input, CI, etc.)
    if not sys.stdin.isatty():
        print("  Non-interactive terminal — defaulting to html")
        return "html"

    selected = 0
    n_items = len(MENU_ITEMS)
    # Menu height: 2 blank + 1 title + 1 blank + n_items + 2 blank + 1 hint + 1 blank = n+8
    menu_lines = n_items + 8

    _render_menu(selected)

    while True:
        key = _getch()

        if key in ("UP", "\x1b[A", "k"):
            selected = (selected - 1) % n_items
        elif key in ("DOWN", "\x1b[B", "j"):
            selected = (selected + 1) % n_items
        elif key in ("\r", "\n", " "):
            # Confirm — erase menu, print summary line
            _clear_menu(menu_lines)
            fmt, label, desc = MENU_ITEMS[selected]
            print(f"  {GREEN}✓{R}  {B}{label}{R}  {GRAY}{desc}{R}\n")
            return fmt
        elif key.lower() == "q":
            _clear_menu(menu_lines)
            print(f"  {GRAY}Cancelled.{R}")
            sys.exit(0)

        _clear_menu(menu_lines)
        _render_menu(selected)
