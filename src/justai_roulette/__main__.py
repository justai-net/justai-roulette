"""JustAI Roulette - RSL Club-style European Roulette Simulator."""

import math
import random
from tkinter import (
    BOTH, LEFT, RIGHT, Frame, IntVar, DoubleVar, BooleanVar,
    StringVar, Tk, Canvas, Spinbox, Label, Toplevel
)
from tkinter import ttk

from .constants import (
    RED_NUMBERS, CHIP_VALUES, Colors, SESSION_FILE, MAX_SINGLE_BET
)
from .game.bets import QUICK_BETS, CALL_BETS
from .audio import play_sound
from .ui.wheel import build_wheel
from .ui.table import build_table
from .ui.theme import setup_styles
from .ui.controls import build_quick_bet_panel, build_action_panel
from .session import load_session, save_session, SessionData


def _fmt_money(amount: float, symbol: str) -> str:
    """Format amount as currency string."""
    return f"{symbol}{amount:,.2f}"


def _roulette_numbers():
    """Iterate European wheel numbers with colors."""
    for n in range(0, 37):
        color = "green" if n == 0 else ("red" if n in RED_NUMBERS else "black")
        yield n, color


def main() -> None:
    """Launch the roulette GUI."""
    root = Tk()
    root.title("JustAI Roulette")
    root.configure(bg=Colors.BG)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    width = max(1220, screen_w - 24)
    height = max(820, screen_h - 32)
    root.geometry(f"{int(width)}x{int(height)}+12+12")
    root.resizable(True, True)

    setup_styles(root)

    # Load session data
    session = load_session()

    # UI State Variables
    result_var = StringVar(value="Place your bets!")
    balance_var = DoubleVar(value=session.balance)
    total_bet_var = DoubleVar(value=0.0)
    winnings_var = DoubleVar(value=0.0)
    countdown_var = IntVar(value=session.auto_spin_interval)
    auto_interval_var = IntVar(value=session.auto_spin_interval)
    session_summary_var = StringVar(value="0 spins")
    breakdown_var = StringVar(value="")
    currency_var = StringVar(value=session.currency)
    sound_enabled = BooleanVar(value=session.sound_enabled)
    auto_enabled = BooleanVar(value=session.auto_spin_enabled)
    selected_chip = DoubleVar(value=CHIP_VALUES[0])

    # Game State
    history_full: list[tuple[int, str]] = list(session.history[:50])
    placed_bets: list[dict] = []
    spinning = {"active": False}
    timer_handle: dict[str, int | None] = {"id": None}
    hot_counts: dict[int, int] = dict(session.hot_counts)
    color_counts: dict[str, int] = dict(session.color_counts)
    parity_counts: dict[str, int] = dict(session.parity_counts)
    session_stats = dict(session.session_stats)
    last_bets: dict = {"items": [], "total": 0}
    last_spin: dict = {"num": None}
    winners_overlay: dict = {"active": False}
    wheel_numbers = tuple(_roulette_numbers())

    auto_interval_var.trace_add("write", lambda *_: countdown_var.set(auto_interval_var.get()))

    # --- Helper Functions ---

    def _save_current_session():
        """Save current state to session file."""
        save_session(SessionData(
            balance=balance_var.get(),
            sound_enabled=sound_enabled.get(),
            auto_spin_enabled=auto_enabled.get(),
            auto_spin_interval=auto_interval_var.get(),
            currency=currency_var.get(),
            history=history_full[:50],
            hot_counts=hot_counts,
            color_counts=color_counts,
            parity_counts=parity_counts,
            session_stats=session_stats,
        ))

    def _update_session_summary():
        profit = session_stats["win_total"] - session_stats["bet_total"]
        session_summary_var.set(
            f"Session: {session_stats['spins']} spins / profit {_fmt_money(profit, currency_var.get())}"
        )

    def _beep(sound_type: str):
        """Play a sound effect."""
        play_sound(sound_type, sound_enabled)

    # --- Winner Flash Overlay ---

    def _clear_winner_flash():
        if winners_overlay.get("timer"):
            root.after_cancel(winners_overlay["timer"])
        canvas = winners_overlay.get("canvas")
        if canvas:
            for cid in winners_overlay.get("ids", []):
                try:
                    canvas.delete(cid)
                except Exception:
                    pass
        winners_overlay.update({
            "active": False, "ids": [], "timer": None,
            "messages": [], "msg_idx": 0, "state": False, "canvas": None
        })

    def _flash_winners():
        if not winners_overlay.get("active"):
            return
        canvas = winners_overlay.get("canvas")
        ids = winners_overlay.get("ids", [])
        if not ids or canvas is None:
            return
        state = winners_overlay.get("state", False)
        for cid in ids:
            canvas.itemconfigure(cid, state="normal" if state else "hidden")
        winners_overlay["state"] = not state
        msgs = winners_overlay.get("messages", [])
        if msgs:
            winners_overlay["msg_idx"] = (winners_overlay.get("msg_idx", 0) + 1) % len(msgs)
            breakdown_var.set(msgs[winners_overlay["msg_idx"]])
        winners_overlay["timer"] = root.after(600, _flash_winners)

    # --- Settings Dialog ---

    def _open_settings():
        win = Toplevel(root)
        win.title("Settings")
        win.configure(bg=Colors.CARD_BG)
        win.transient(root)
        win.grab_set()
        win.geometry(f"340x480+{root.winfo_x() + 100}+{root.winfo_y() + 50}")

        frame = Frame(win, bg=Colors.CARD_BG)
        frame.pack(fill=BOTH, expand=True, padx=16, pady=16)

        Label(frame, text="Settings", font=("Segoe UI", 16, "bold"),
              fg=Colors.ACCENT, bg=Colors.CARD_BG).pack(anchor="w", pady=(0, 12))

        # Auto-Spin
        Label(frame, text="AUTO-SPIN", font=("Segoe UI", 10, "bold"),
              fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w", pady=(8, 4))
        auto_frame = Frame(frame, bg=Colors.CARD_BG)
        auto_frame.pack(fill="x", pady=(0, 8))
        ttk.Checkbutton(auto_frame, text="Enable auto-spin", variable=auto_enabled,
                        style="Game.TCheckbutton", command=schedule_countdown).pack(side=LEFT)
        Label(auto_frame, text="Interval:", fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG,
              font=("Segoe UI", 10)).pack(side=LEFT, padx=(12, 4))
        Spinbox(auto_frame, from_=10, to=120, width=4, textvariable=auto_interval_var,
                bg=Colors.BUTTON_BG, fg=Colors.TEXT_LIGHT, highlightthickness=0, bd=0,
                font=("Segoe UI", 10)).pack(side=LEFT)
        Label(auto_frame, text="s", fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG,
              font=("Segoe UI", 10)).pack(side=LEFT)

        # Sound
        Label(frame, text="AUDIO", font=("Segoe UI", 10, "bold"),
              fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w", pady=(8, 4))
        ttk.Checkbutton(frame, text="Enable sound effects", variable=sound_enabled,
                        style="Game.TCheckbutton").pack(anchor="w")

        # Currency
        Label(frame, text="CURRENCY", font=("Segoe UI", 10, "bold"),
              fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w", pady=(12, 4))
        curr_frame = Frame(frame, bg=Colors.CARD_BG)
        curr_frame.pack(fill="x", pady=(0, 8))
        for sym in ["$", "EUR", "£"]:
            ttk.Radiobutton(curr_frame, text=sym if sym != "EUR" else "€",
                           variable=currency_var, value=sym,
                           style="Game.TCheckbutton").pack(side=LEFT, padx=(0, 12))

        # Session
        Label(frame, text="SESSION", font=("Segoe UI", 10, "bold"),
              fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w", pady=(12, 4))
        add_row = Frame(frame, bg=Colors.CARD_BG)
        add_row.pack(fill="x", pady=(0, 8))
        Label(add_row, text="Add balance:", fg=Colors.TEXT_LIGHT, bg=Colors.CARD_BG,
              font=("Segoe UI", 10)).pack(side=LEFT)
        add_amount = StringVar(value="100")
        Spinbox(add_row, from_=0, to=100000, textvariable=add_amount, width=8,
                bg=Colors.BUTTON_BG, fg=Colors.TEXT_LIGHT, highlightthickness=0, bd=0).pack(side=LEFT, padx=8)

        def _apply_add():
            try:
                amt = float(add_amount.get())
                if amt > 0:
                    balance_var.set(balance_var.get() + amt)
                    _save_current_session()
            except ValueError:
                pass

        ttk.Button(add_row, text="Add", command=_apply_add, width=6).pack(side=LEFT)
        ttk.Button(frame, text="Reset Session",
                   command=lambda: (_reset_session(), win.destroy()), width=20).pack(anchor="w", pady=(4, 0))

        # Help
        Label(frame, text="HELP", font=("Segoe UI", 10, "bold"),
              fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w", pady=(16, 4))
        Label(frame, text="Straight: 35:1 • Split: 17:1 • Corner: 8:1\nDozen/Column: 2:1 • Even money: 1:1",
              font=("Segoe UI", 9), fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG,
              justify="left").pack(anchor="w")

        ttk.Button(frame, text="Close", command=win.destroy,
                   style="Accent.TButton", width=12).pack(anchor="e", pady=(16, 0))

    # --- Build UI Layout ---

    # Main game container
    game_frame = Frame(root, bg=Colors.FELT)
    game_frame.pack(fill=BOTH, expand=True)

    # Top HUD bar
    hud_bar = Frame(game_frame, bg=Colors.CARD_BG, height=72)
    hud_bar.pack(fill="x")
    hud_bar.pack_propagate(False)

    # Money displays
    money_frame = Frame(hud_bar, bg=Colors.CARD_BG)
    money_frame.pack(side=LEFT, padx=20, pady=8)

    # Balance
    balance_inner = Frame(money_frame, bg=Colors.CARD_BG)
    balance_inner.pack(side=LEFT, padx=(0, 28))
    Label(balance_inner, text="BALANCE", font=("Segoe UI", 10, "bold"),
          fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w")
    balance_label = Label(balance_inner, text=_fmt_money(balance_var.get(), currency_var.get()),
                          font=("Segoe UI", 22, "bold"), fg="#3fe68b", bg=Colors.CARD_BG)
    balance_label.pack(anchor="w")
    balance_var.trace_add("write", lambda *_: balance_label.config(
        text=_fmt_money(balance_var.get(), currency_var.get())))

    # Bet
    bet_inner = Frame(money_frame, bg=Colors.CARD_BG)
    bet_inner.pack(side=LEFT, padx=(0, 28))
    Label(bet_inner, text="BET", font=("Segoe UI", 10, "bold"),
          fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w")
    bet_label = Label(bet_inner, text="$0.00", font=("Segoe UI", 22, "bold"),
                      fg="#ff7b7b", bg=Colors.CARD_BG)
    bet_label.pack(anchor="w")
    total_bet_var.trace_add("write", lambda *_: bet_label.config(
        text=_fmt_money(total_bet_var.get(), currency_var.get())))

    # Win
    win_inner = Frame(money_frame, bg=Colors.CARD_BG)
    win_inner.pack(side=LEFT, padx=(0, 28))
    Label(win_inner, text="WIN", font=("Segoe UI", 10, "bold"),
          fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w")
    win_label = Label(win_inner, text="$0.00", font=("Segoe UI", 22, "bold"),
                      fg="#54a7ff", bg=Colors.CARD_BG)
    win_label.pack(anchor="w")
    winnings_var.trace_add("write", lambda *_: win_label.config(
        text=_fmt_money(winnings_var.get(), currency_var.get())))

    # Session
    session_inner = Frame(money_frame, bg=Colors.CARD_BG)
    session_inner.pack(side=LEFT)
    Label(session_inner, text="SESSION", font=("Segoe UI", 10, "bold"),
          fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack(anchor="w")
    Label(session_inner, textvariable=session_summary_var, font=("Segoe UI", 12),
          fg=Colors.TEXT_LIGHT, bg=Colors.CARD_BG).pack(anchor="w")

    # Center: Result display
    center_hud = Frame(hud_bar, bg=Colors.CARD_BG)
    center_hud.pack(side=LEFT, fill="x", expand=True, padx=20)
    Label(center_hud, textvariable=result_var, font=("Segoe UI", 15, "bold"),
          fg=Colors.ACCENT, bg=Colors.CARD_BG).pack(pady=(8, 0))
    Label(center_hud, textvariable=breakdown_var, font=("Segoe UI", 11),
          fg=Colors.TEXT_MUTED, bg=Colors.CARD_BG).pack()

    # Right: Settings button
    right_hud = Frame(hud_bar, bg=Colors.CARD_BG)
    right_hud.pack(side=RIGHT, padx=20, pady=8)
    ttk.Button(right_hud, text="Settings", command=_open_settings, width=10).pack()

    # Wooden table frame
    wood_border = Frame(game_frame, bg=Colors.WOOD_DARK)
    wood_border.pack(fill=BOTH, expand=True, padx=12, pady=8)
    wood_inner = Frame(wood_border, bg=Colors.WOOD_MID)
    wood_inner.pack(fill=BOTH, expand=True, padx=6, pady=6)
    gold_trim = Frame(wood_inner, bg=Colors.ACCENT)
    gold_trim.pack(fill=BOTH, expand=True, padx=3, pady=3)
    felt_surface = Frame(gold_trim, bg=Colors.FELT)
    felt_surface.pack(fill=BOTH, expand=True, padx=2, pady=2)

    # Main table row
    table_row = Frame(felt_surface, bg=Colors.FELT)
    table_row.pack(fill=BOTH, expand=True, padx=4, pady=4)
    table_row.grid_columnconfigure(0, weight=0)
    table_row.grid_columnconfigure(1, weight=1)
    table_row.grid_rowconfigure(0, weight=1)

    # Wheel section
    wheel_section = Frame(table_row, bg=Colors.FELT)
    wheel_section.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    countdown_section = Frame(wheel_section, bg=Colors.FELT)
    countdown_section.pack(fill="x", pady=(0, 8))
    Label(countdown_section, text="NEXT SPIN", font=("Segoe UI", 12, "bold"),
          fg=Colors.TEXT_MUTED, bg=Colors.FELT).pack()
    Label(countdown_section, textvariable=countdown_var, font=("Segoe UI", 36, "bold"),
          fg=Colors.ACCENT, bg=Colors.FELT).pack()

    wheel_container = Frame(wheel_section, bg=Colors.FELT)
    wheel_container.pack(fill=BOTH, expand=True)
    wheel_ui = build_wheel(wheel_container)

    # Table area
    table_area = Frame(table_row, bg=Colors.FELT)
    table_area.grid(row=0, column=1, sticky="nsew")

    # --- Bet Selection Handler ---

    def _set_selection(label: str, numbers: list[int], payout: int,
                       key: tuple[int, ...], x: float, y: float, mark_cb):
        if spinning["active"]:
            result_var.set("Wait for spin...")
            return
        if winners_overlay["active"]:
            _clear_winner_flash()
            clear_markers()

        amount = selected_chip.get()
        if total_bet_var.get() + amount > balance_var.get():
            result_var.set("Insufficient balance!")
            return
        if amount > MAX_SINGLE_BET:
            result_var.set(f"Max bet: {_fmt_money(MAX_SINGLE_BET, currency_var.get())}")
            return

        existing = next((b for b in placed_bets if b["key"] == key), None)
        if existing:
            existing["amount"] += amount
            marker_amount = existing["amount"]
        else:
            placed_bets.append({
                "label": label, "numbers": numbers, "payout": payout,
                "amount": amount, "key": key, "x": x, "y": y
            })
            marker_amount = amount

        total_bet_var.set(total_bet_var.get() + amount)
        mark_cb(key, marker_amount, x, y)

    # History strip
    history_canvas = Canvas(table_area, bg=Colors.FELT, highlightthickness=0, height=56)
    history_canvas.pack(fill="x", pady=(0, 4))

    def _draw_history_chips():
        history_canvas.delete("all")
        w = history_canvas.winfo_width()
        if w < 10:
            w = 600
        chip_r, spacing, start_x, cy = 22, 52, 8, 28

        for i, (num, _) in enumerate(history_full[:12]):
            cx = start_x + i * spacing + chip_r
            if cx + chip_r > w - 10:
                break
            color = "#0ecf6e" if num == 0 else ("#c0392b" if num in RED_NUMBERS else "#1c1c1c")
            history_canvas.create_oval(cx - chip_r + 2, cy - chip_r + 2,
                                       cx + chip_r + 2, cy + chip_r + 2, fill="#1a1a1a", outline="")
            history_canvas.create_oval(cx - chip_r, cy - chip_r, cx + chip_r, cy + chip_r,
                                       fill=color, outline="#ffd700", width=2)
            history_canvas.create_text(cx, cy, text=str(num), font=("Segoe UI", 12, "bold"), fill="#fff")

    history_canvas.bind("<Configure>", lambda e: _draw_history_chips())

    # Betting table
    table_frame = Frame(table_area, bg=Colors.FELT)
    table_frame.pack(fill=BOTH, expand=True)
    (clear_markers, place_marker, number_centers, outside_bet_centers,
     table_canvas, scale_table_point) = build_table(table_frame, _set_selection)

    # Bottom section
    bottom_section = Frame(table_area, bg=Colors.FELT)
    bottom_section.pack(fill="x")

    # Chip tray
    chip_tray_canvas = Canvas(bottom_section, bg=Colors.FELT, highlightthickness=0, height=90)
    chip_tray_canvas.pack(fill="x", padx=4, pady=(6, 4))
    chip_buttons = {}

    def _draw_chip_tray():
        chip_tray_canvas.delete("all")
        w = chip_tray_canvas.winfo_width()
        if w < 10:
            w = 700
        chip_r, spacing = 34, 84
        total_width = len(CHIP_VALUES) * spacing
        start_x = (w - total_width) // 2 + chip_r + 8
        cy = 45

        chip_styles = [
            {"fill": "#dc143c", "edge": "#fff", "stripe": "#fff"},
            {"fill": "#1e90ff", "edge": "#fff", "stripe": "#fff"},
            {"fill": "#228b22", "edge": "#fff", "stripe": "#fff"},
            {"fill": "#8b008b", "edge": "#ffd700", "stripe": "#ffd700"},
            {"fill": "#ff8c00", "edge": "#000", "stripe": "#000"},
            {"fill": "#2f4f4f", "edge": "#ffd700", "stripe": "#ffd700"},
        ]

        for i, value in enumerate(CHIP_VALUES):
            cx = start_x + i * spacing
            style = chip_styles[i % len(chip_styles)]
            is_selected = abs(selected_chip.get() - value) < 0.01

            # Shadow and chip body
            chip_tray_canvas.create_oval(cx - chip_r + 3, cy - chip_r + 3,
                                         cx + chip_r + 3, cy + chip_r + 3, fill="#0a0a0a", outline="")
            chip_tray_canvas.create_oval(cx - chip_r, cy - chip_r, cx + chip_r, cy + chip_r,
                                         fill=style["fill"], outline=style["edge"], width=2)

            # Edge stripes
            stripe_r = chip_r - 2
            for angle_deg in range(0, 360, 45):
                angle = math.radians(angle_deg)
                sx = cx + stripe_r * math.cos(angle)
                sy = cy + stripe_r * math.sin(angle)
                chip_tray_canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4,
                                             fill=style["stripe"], outline="")

            # Inner rings
            inner_r1 = chip_r - 10
            chip_tray_canvas.create_oval(cx - inner_r1, cy - inner_r1, cx + inner_r1, cy + inner_r1,
                                         fill="", outline=style["edge"], width=2)
            inner_r2 = chip_r - 14
            chip_tray_canvas.create_oval(cx - inner_r2, cy - inner_r2, cx + inner_r2, cy + inner_r2,
                                         fill=style["fill"], outline="")

            # Value text
            txt = f"${value:.0f}" if value >= 1 else "50¢"
            chip_tray_canvas.create_text(cx, cy, text=txt, font=("Segoe UI", 12, "bold"), fill="#fff")

            # Selection glow
            if is_selected:
                glow_r = chip_r + 4
                chip_tray_canvas.create_oval(cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                                             fill="", outline="#ffd700", width=3)

            chip_buttons[i] = {"bounds": (cx - chip_r - 4, cy - chip_r - 4,
                                          cx + chip_r + 4, cy + chip_r + 4), "value": value}

    def _on_chip_click(event):
        for data in chip_buttons.values():
            x0, y0, x1, y1 = data["bounds"]
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                selected_chip.set(data["value"])
                _draw_chip_tray()
                return

    chip_tray_canvas.bind("<ButtonRelease-1>", _on_chip_click)
    chip_tray_canvas.bind("<Configure>", lambda e: _draw_chip_tray())

    # --- Bet Management Functions ---

    def clear_bets():
        placed_bets.clear()
        total_bet_var.set(0)
        clear_markers()
        _clear_winner_flash()

    def _reset_session():
        clear_bets()
        balance_var.set(100.0)
        winnings_var.set(0.0)
        session_stats.update({"spins": 0, "bet_total": 0.0, "win_total": 0.0})
        hot_counts.clear()
        color_counts.update({"red": 0, "black": 0, "green": 0})
        parity_counts.update({"odd": 0, "even": 0, "zero": 0})
        history_full.clear()
        _draw_history_chips()
        _update_session_summary()
        result_var.set("Session reset.")
        _save_current_session()

    def _redraw_markers():
        clear_markers()
        total_bet_var.set(0)
        for bet in placed_bets:
            total_bet_var.set(total_bet_var.get() + bet["amount"])
            place_marker(bet["key"], bet["amount"], bet.get("x", 0), bet.get("y", 0))

    def undo_last():
        if spinning["active"] or not placed_bets:
            return
        placed_bets.pop()
        if not placed_bets:
            clear_bets()
        else:
            _redraw_markers()

    def rebet_previous():
        if spinning["active"] or not last_bets["items"]:
            return
        if last_bets["total"] > balance_var.get():
            result_var.set("Insufficient balance to re-bet.")
            return
        placed_bets.clear()
        total_bet_var.set(0)
        for bet in last_bets["items"]:
            placed_bets.append(dict(bet))
        _redraw_markers()

    def _double_bets():
        if spinning["active"] or not placed_bets:
            return
        current_total = total_bet_var.get()
        if current_total * 2 > balance_var.get():
            result_var.set("Insufficient balance to double.")
            return
        for bet in placed_bets:
            bet["amount"] *= 2
        total_bet_var.set(current_total * 2)
        _beep("chip_place")

    # --- Quick Bet Functions ---

    def _quick_bet(bet_name: str):
        if spinning["active"]:
            return
        if winners_overlay["active"]:
            _clear_winner_flash()
            clear_markers()

        chip_amount = selected_chip.get()

        if bet_name in CALL_BETS:
            _place_call_bet(bet_name, chip_amount)
            return

        if bet_name not in QUICK_BETS:
            return
        numbers, payout = QUICK_BETS[bet_name]

        if total_bet_var.get() + chip_amount > balance_var.get():
            result_var.set("Insufficient balance.")
            return

        cx, cy = outside_bet_centers.get(bet_name, (wheel_ui["cx"], wheel_ui["cy"]))
        key = tuple(sorted(numbers))

        existing = next((b for b in placed_bets if b["key"] == key), None)
        if existing:
            existing["amount"] += chip_amount
            marker_amount = existing["amount"]
        else:
            placed_bets.append({
                "label": bet_name, "numbers": numbers, "payout": payout,
                "amount": chip_amount, "key": key, "x": cx, "y": cy,
            })
            marker_amount = chip_amount

        place_marker(key, marker_amount, cx, cy)
        total_bet_var.set(total_bet_var.get() + chip_amount)
        _beep("chip_place")

    def _place_call_bet(bet_name: str, chip_amount: float):
        bets = CALL_BETS[bet_name]
        total_chips = sum(c for _, _, c in bets)
        total_cost = chip_amount * total_chips

        if total_bet_var.get() + total_cost > balance_var.get():
            result_var.set(f"Need {total_chips} chips for {bet_name}.")
            return

        for numbers, payout, chip_count in bets:
            bet_amount = chip_amount * chip_count
            key = tuple(sorted(numbers))

            if len(numbers) == 1 and numbers[0] in number_centers:
                cx, cy = number_centers[numbers[0]]
            elif all(n in number_centers for n in numbers):
                xs = [number_centers[n][0] for n in numbers]
                ys = [number_centers[n][1] for n in numbers]
                cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
            else:
                cx, cy = wheel_ui["cx"], wheel_ui["cy"]

            if len(numbers) == 1:
                label = f"Straight {numbers[0]}"
            elif len(numbers) == 2:
                label = f"Split {numbers[0]}/{numbers[1]}"
            else:
                label = f"{bet_name} bet"

            existing = next((b for b in placed_bets if b["key"] == key), None)
            if existing:
                existing["amount"] += bet_amount
                marker_amount = existing["amount"]
            else:
                placed_bets.append({
                    "label": label, "numbers": list(numbers), "payout": payout,
                    "amount": bet_amount, "key": key, "x": cx, "y": cy,
                })
                marker_amount = bet_amount

            place_marker(key, marker_amount, cx, cy)

        total_bet_var.set(total_bet_var.get() + total_cost)
        _beep("chip_place")

    # Controls
    controls_row = Frame(bottom_section, bg=Colors.FELT)
    controls_row.pack(fill="x", padx=6, pady=(0, 8))

    quick_bet_panel = build_quick_bet_panel(controls_row, _quick_bet, Colors.FELT)
    quick_bet_panel.pack(side=LEFT, fill="x", expand=True)

    action_panel = build_action_panel(
        controls_row,
        on_rebet=rebet_previous,
        on_double=_double_bets,
        on_undo=undo_last,
        on_clear=clear_bets,
        on_spin=lambda: run_spin(),
        bg_color=Colors.FELT,
    )
    action_panel.pack(side=RIGHT, padx=(12, 0))

    # --- Spin Logic ---

    def finish_spin(final_number: int, final_color: str, bet_snapshot: list[dict], bet_amount: float):
        balance = balance_var.get() - bet_amount
        total_win = 0
        max_payout = 0

        for bet in bet_snapshot:
            if final_number in bet["numbers"]:
                win = bet["amount"] * (bet["payout"] + 1)
                total_win += win
                max_payout = max(max_payout, bet["payout"])

        winnings_var.set(total_win)
        is_big_win = total_win >= bet_amount * 10 or max_payout >= 35

        if total_win > 0:
            balance += total_win
            _beep("big_win" if is_big_win else "win")
            prefix = "BIG WIN!" if is_big_win else "WIN!"
            result_var.set(f"{prefix} {final_number} ({final_color}) - {_fmt_money(total_win, currency_var.get())}")
        else:
            result_var.set(f"Result: {final_number} ({final_color})")

        balance_var.set(balance)
        session_stats["spins"] += 1
        session_stats["bet_total"] += bet_amount
        session_stats["win_total"] += total_win
        _update_session_summary()

        history_full.insert(0, (final_number, final_color))
        del history_full[50:]
        _draw_history_chips()

        hot_counts[final_number] = hot_counts.get(final_number, 0) + 1
        color_counts[final_color] = color_counts.get(final_color, 0) + 1
        last_spin["num"] = final_number

        _clear_winner_flash()
        clear_markers()

        winners = [b for b in bet_snapshot if final_number in b["numbers"]]
        if winners:
            winners_overlay["active"] = True
            winners_overlay["canvas"] = table_canvas
            winners_overlay["ids"] = []
            winners_overlay["messages"] = [
                f"{b['label']}: {_fmt_money(b['amount'] * (b['payout'] + 1), currency_var.get())}"
                for b in winners
            ]

            for wb in winners:
                place_marker(wb["key"], wb["amount"], wb.get("x", 0), wb.get("y", 0))
                sx, sy, sr = scale_table_point(wb.get("x", 0), wb.get("y", 0), 18)
                cid = table_canvas.create_oval(sx - sr, sy - sr, sx + sr, sy + sr,
                                               outline=Colors.ACCENT, width=3)
                winners_overlay["ids"].append(cid)

            winners_overlay["timer"] = root.after(600, _flash_winners)
        else:
            breakdown_var.set("Better luck next spin!")

        placed_bets.clear()
        total_bet_var.set(0)
        spinning["active"] = False
        _save_current_session()
        schedule_countdown(reset=False)

    def animate_bounce(bounces, angle, final_number, final_color, bet_snapshot, bet_amount):
        if bounces:
            radius, delay = bounces.pop(0)
            wheel_ui["move_ball"](angle, radius=radius)
            _beep("ball_click")
            root.after(int(delay), animate_bounce, bounces, angle,
                      final_number, final_color, bet_snapshot, bet_amount)
        else:
            wheel_ui["show_result"](final_number, final_color)
            finish_spin(final_number, final_color, bet_snapshot, bet_amount)

    def animate_drop(step, steps, angle, final_number, final_color, bet_snapshot, bet_amount):
        progress = step / steps
        outer_r = wheel_ui.get("ball_track_radius", wheel_ui["outer_radius"])
        inner_r = wheel_ui["outer_radius"] * 0.3
        radius = outer_r - (outer_r - inner_r) * (progress ** 0.8)

        wheel_ui["move_ball"](angle, radius=radius)

        if step < steps:
            delay = 40 + int(progress * 60)
            root.after(delay, animate_drop, step + 1, steps, angle,
                      final_number, final_color, bet_snapshot, bet_amount)
        else:
            target_r = wheel_ui["outer_radius"] * 0.35
            bounces = [(target_r + 15, 120), (target_r + 5, 100),
                      (target_r + 8, 80), (target_r, 60)]
            animate_bounce(bounces, angle, final_number, final_color, bet_snapshot, bet_amount)

    def animate_spin(angles, final_number, final_color, bet_snapshot, bet_amount):
        if angles:
            ang = angles.pop(0)
            wheel_ui["move_ball"](ang, on_track=True)
            n, c = random.choice(wheel_numbers)
            result_var.set(f"Spinning... {n} ({c})")
            delay = 30 + int((1 - len(angles) / 50) * 40)
            root.after(delay, animate_spin, angles, final_number, final_color, bet_snapshot, bet_amount)
        else:
            target_angle = wheel_ui["number_to_angle"][final_number]
            result_var.set("Ball dropping...")
            animate_drop(0, 12, target_angle, final_number, final_color, bet_snapshot, bet_amount)

    def run_spin():
        if spinning["active"]:
            return
        _cancel_countdown()
        countdown_var.set(auto_interval_var.get())

        bet_amount = total_bet_var.get()
        if bet_amount > 0 and placed_bets and bet_amount <= balance_var.get():
            bet_snapshot = [dict(b) for b in placed_bets]
            last_bets["items"] = [dict(b) for b in bet_snapshot]
            last_bets["total"] = bet_amount
        else:
            bet_snapshot = []
            bet_amount = 0
            placed_bets.clear()
            total_bet_var.set(0)

        final_number, final_color = random.choice(wheel_numbers)
        spinning["active"] = True
        _beep("spin_start")

        target_angle = wheel_ui["number_to_angle"][final_number]
        rotations = 3 + random.randint(0, 2)
        start_angle = target_angle + 2 * math.pi * rotations + random.random() * 2 * math.pi

        angles = []
        for i in range(40):
            t = (i + 1) / 40
            ang = start_angle - (start_angle - target_angle) * (t ** 1.5)
            angles.append(ang)

        wheel_ui["reset"]()
        animate_spin(angles, final_number, final_color, bet_snapshot, bet_amount)

    # --- Countdown Timer ---

    def _cancel_countdown():
        if timer_handle["id"] is not None:
            root.after_cancel(timer_handle["id"])
            timer_handle["id"] = None

    def tick():
        if not auto_enabled.get() or spinning["active"]:
            if auto_enabled.get():
                timer_handle["id"] = root.after(1000, tick)
            return
        remaining = countdown_var.get()
        if remaining > 0:
            countdown_var.set(remaining - 1)
            timer_handle["id"] = root.after(1000, tick)
        else:
            countdown_var.set(auto_interval_var.get())
            run_spin()

    def schedule_countdown(reset: bool = True):
        _cancel_countdown()
        if not auto_enabled.get():
            return
        if reset:
            countdown_var.set(auto_interval_var.get())
        timer_handle["id"] = root.after(1000, tick)

    # --- Keyboard Input ---

    key_buffer = {"digits": "", "timer": None}

    def _on_key(event):
        if not event.char.isdigit():
            return
        key_buffer["digits"] += event.char
        if key_buffer["timer"]:
            root.after_cancel(key_buffer["timer"])
        key_buffer["timer"] = root.after(700, lambda: key_buffer.update({"digits": "", "timer": None}))
        try:
            val = int(key_buffer["digits"])
            if 0 <= val <= 36 and val in number_centers:
                cx, cy = number_centers[val]
                _set_selection(f"Straight {val}", [val], 35, (val,), cx, cy, place_marker)
                key_buffer.update({"digits": "", "timer": None})
        except ValueError:
            pass

    root.bind("<Key>", _on_key)

    # --- Initialize ---

    _draw_chip_tray()
    _draw_history_chips()
    _update_session_summary()
    schedule_countdown()

    root.update_idletasks()
    root.minsize(min(screen_w - 16, root.winfo_reqwidth()),
                 min(screen_h - 16, root.winfo_reqheight()))
    root.protocol("WM_DELETE_WINDOW", lambda: (_save_current_session(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
