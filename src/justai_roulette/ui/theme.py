"""TTK styling and theme configuration."""

import sys
from tkinter import ttk
from ..constants import Colors


def setup_styles(root) -> ttk.Style:
    """Configure all TTK styles for the application."""
    style = ttk.Style()

    # Force 'clam' theme on all platforms for consistent button colors
    # macOS 'aqua' theme ignores background color settings
    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')
    elif 'alt' in available_themes:
        style.theme_use('alt')
    # else: use default

    # Helper to configure button styles consistently
    def _configure_button(name, bg, fg, active_bg, font_size=10):
        style.configure(
            name,
            background=bg,
            foreground=fg,
            borderwidth=1,
            relief="raised",
            focusthickness=0,
            focuscolor="none",
            font=("Segoe UI", font_size, "bold"),
            padding=(8, 6),
        )
        style.map(
            name,
            background=[("active", active_bg), ("pressed", active_bg), ("!disabled", bg)],
            foreground=[("active", fg), ("!disabled", fg)],
            relief=[("pressed", "sunken"), ("!pressed", "raised")],
        )

    # Main button style
    _configure_button("Game.TButton", Colors.BUTTON_BG, Colors.TEXT_LIGHT, Colors.BUTTON_ACTIVE, 11)

    # Accent button style (for SPIN) - Large and prominent
    style.configure(
        "Accent.TButton",
        background=Colors.ACCENT,
        foreground="#1a1a1a",
        borderwidth=2,
        relief="raised",
        focusthickness=0,
        focuscolor="none",
        font=("Segoe UI", 16, "bold"),
        padding=(20, 12),
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#ffdf00"), ("pressed", "#e6c200"), ("!disabled", Colors.ACCENT)],
        foreground=[("active", "#1a1a1a"), ("!disabled", "#1a1a1a")],
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
    )

    # Quick bet button styles
    _configure_button("QuickBet.TButton", Colors.BUTTON_BG, Colors.TEXT_LIGHT, Colors.BUTTON_ACTIVE)

    # Red button
    _configure_button("Red.TButton", "#c0392b", "white", "#e74c3c")

    # Black button
    _configure_button("Black.TButton", "#1c1c1c", "white", "#333333")

    # Green button
    _configure_button("Green.TButton", "#0a5c36", "white", "#0d7a48")

    # Dark green button
    _configure_button("DarkGreen.TButton", "#145a32", "white", "#1a7a42")

    # Call bet style (gold/amber for European wheel-position bets)
    _configure_button("CallBet.TButton", "#b8860b", "white", "#daa520")

    # Checkbutton style
    style.configure(
        "Game.TCheckbutton",
        background=Colors.CARD_BG,
        foreground=Colors.TEXT_LIGHT,
        font=("Segoe UI", 10),
        indicatorbackground=Colors.BUTTON_BG,
        indicatorforeground=Colors.ACCENT,
    )
    style.map(
        "Game.TCheckbutton",
        background=[("active", Colors.CARD_BG)],
        indicatorbackground=[("selected", Colors.ACCENT)],
    )

    return style
