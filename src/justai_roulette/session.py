"""Session persistence for JustAI Roulette."""

import json
from dataclasses import dataclass, field
from typing import Any

from .constants import SESSION_FILE, DEFAULT_BALANCE


@dataclass
class SessionData:
    """Session state that persists between runs."""
    balance: float = DEFAULT_BALANCE
    sound_enabled: bool = False
    auto_spin_enabled: bool = True
    auto_spin_interval: int = 40
    currency: str = "$"
    history: list[tuple[int, str]] = field(default_factory=list)
    hot_counts: dict[int, int] = field(default_factory=dict)
    color_counts: dict[str, int] = field(default_factory=lambda: {"red": 0, "black": 0, "green": 0})
    parity_counts: dict[str, int] = field(default_factory=lambda: {"odd": 0, "even": 0, "zero": 0})
    session_stats: dict[str, Any] = field(default_factory=lambda: {"spins": 0, "bet_total": 0.0, "win_total": 0.0})


def load_session() -> SessionData:
    """Load session from file, returning defaults if not found."""
    try:
        if SESSION_FILE.exists():
            data = json.loads(SESSION_FILE.read_text())

            # Parse history - handle both old and new formats
            history = []
            for entry in data.get("history", []):
                if isinstance(entry, dict) and "n" in entry and "c" in entry:
                    # Old format: {"n": 5, "c": "red"}
                    history.append((int(entry["n"]), str(entry["c"])))
                elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                    # New format: [5, "red"]
                    history.append((int(entry[0]), str(entry[1])))

            # Convert hot_counts keys back to integers
            hot_counts = {}
            for k, v in data.get("hot_counts", {}).items():
                try:
                    hot_counts[int(k)] = v
                except (ValueError, TypeError):
                    pass

            return SessionData(
                balance=data.get("balance", DEFAULT_BALANCE),
                sound_enabled=data.get("sound_enabled", False),
                auto_spin_enabled=data.get("auto_spin_enabled", data.get("auto_enabled", True)),
                auto_spin_interval=data.get("auto_spin_interval", data.get("auto_interval", 40)),
                currency=data.get("currency", "$"),
                history=history[:50],
                hot_counts=hot_counts,
                color_counts=data.get("color_counts", {"red": 0, "black": 0, "green": 0}),
                parity_counts=data.get("parity_counts", {"odd": 0, "even": 0, "zero": 0}),
                session_stats=data.get("session_stats", {"spins": 0, "bet_total": 0.0, "win_total": 0.0}),
            )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        pass
    return SessionData()


def save_session(session: SessionData) -> None:
    """Save session to file."""
    try:
        data = {
            "balance": session.balance,
            "sound_enabled": session.sound_enabled,
            "auto_spin_enabled": session.auto_spin_enabled,
            "auto_spin_interval": session.auto_spin_interval,
            "currency": session.currency,
            "history": [list(h) for h in session.history[:50]],
            "hot_counts": {str(k): v for k, v in session.hot_counts.items()},
            "color_counts": session.color_counts,
            "parity_counts": session.parity_counts,
            "session_stats": session.session_stats,
        }
        SESSION_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass
