"""Game control buttons and quick bet UI components."""

from tkinter import Frame, LEFT
from tkinter import ttk
from typing import Callable

from ..constants import Colors


def build_quick_bet_panel(parent: Frame, on_bet: Callable[[str], None], bg_color: str = Colors.FELT) -> Frame:
    """Build the quick bet button panel."""
    frame = Frame(parent, bg=bg_color)

    # Row 1: Color and even-money bets
    row1 = Frame(frame, bg=bg_color)
    row1.pack(fill="x", pady=2)

    bets_row1 = [
        ("RED", "Red", "Red.TButton"),
        ("BLACK", "Black", "Black.TButton"),
        ("ODD", "Odd", "Game.TButton"),
        ("EVEN", "Even", "Game.TButton"),
        ("1-18", "1-18", "Game.TButton"),
        ("19-36", "19-36", "Game.TButton"),
        ("1st 12", "1st 12", "Green.TButton"),
        ("2nd 12", "2nd 12", "Green.TButton"),
        ("3rd 12", "3rd 12", "Green.TButton"),
    ]

    for text, bet_name, style in bets_row1:
        btn = ttk.Button(row1, text=text, command=lambda b=bet_name: on_bet(b), width=7, style=style)
        btn.pack(side=LEFT, padx=2)

    # Row 2: Columns and call bets
    row2 = Frame(frame, bg=bg_color)
    row2.pack(fill="x", pady=2)

    bets_row2 = [
        ("Col 1", "Col 1", "DarkGreen.TButton"),
        ("Col 2", "Col 2", "DarkGreen.TButton"),
        ("Col 3", "Col 3", "DarkGreen.TButton"),
        ("Voisins", "Voisins", "CallBet.TButton"),
        ("Tiers", "Tiers", "CallBet.TButton"),
        ("Orphelins", "Orphelins", "CallBet.TButton"),
        ("Jeu Zéro", "Jeu Zéro", "CallBet.TButton"),
    ]

    for text, bet_name, style in bets_row2:
        btn = ttk.Button(row2, text=text, command=lambda b=bet_name: on_bet(b), width=8, style=style)
        btn.pack(side=LEFT, padx=2)

    return frame


def build_action_panel(
    parent: Frame,
    on_rebet: Callable[[], None],
    on_double: Callable[[], None],
    on_undo: Callable[[], None],
    on_clear: Callable[[], None],
    on_spin: Callable[[], None],
    bg_color: str = Colors.FELT,
) -> Frame:
    """Build the action button panel (Re-bet, 2x, Undo, Clear, SPIN)."""
    frame = Frame(parent, bg=bg_color)

    # Utility buttons row
    util_row = Frame(frame, bg=bg_color)
    util_row.pack(fill="x", pady=2)

    ttk.Button(util_row, text="Re-bet", command=on_rebet, width=7, style="Game.TButton").pack(side=LEFT, padx=2)
    ttk.Button(util_row, text="2x", command=on_double, width=4, style="Game.TButton").pack(side=LEFT, padx=2)
    ttk.Button(util_row, text="Undo", command=on_undo, width=6, style="Game.TButton").pack(side=LEFT, padx=2)
    ttk.Button(util_row, text="Clear", command=on_clear, width=6, style="Game.TButton").pack(side=LEFT, padx=2)

    # SPIN button - prominent styling
    spin_btn = ttk.Button(frame, text="SPIN", command=on_spin, style="Accent.TButton")
    spin_btn.pack(fill="x", padx=2, pady=(4, 0))

    return frame
