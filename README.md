# JustAI Roulette

RSL Club-style European Roulette Simulator built with Python/Tkinter.

## Features

- **Authentic RSL Club Styling**: Burgundy/maroon color scheme with gold accents
- **Chrome Machine Bezels**: Realistic electronic gaming machine appearance
- **European Single-Zero Wheel**: Authentic 37-pocket wheel with correct number ordering
- **3D Chip Visuals**: Casino-style chips with shadows and highlights
- **Realistic Spin Animation**: Ball track, bouncing physics, and suspenseful slowdown
- **Quick Bet Buttons**: One-touch betting for Red/Black, Odd/Even, Dozens, Columns
- **Win Celebrations**: Animated effects for wins with "BIG WIN" for straight-up hits
- **Session Persistence**: Balance and history saved between sessions
- **Auto-Spin**: Configurable automatic spin timer (10-120 seconds)
- **Cross-Platform Audio**: Sound effects with fallback support

## Bet Types

| Bet Type | Payout | Description |
|----------|--------|-------------|
| Straight | 35:1 | Single number |
| Split | 17:1 | Two adjacent numbers |
| Corner | 8:1 | Four numbers at intersection |
| Column | 2:1 | 12 numbers in vertical column |
| Dozen | 2:1 | 1-12, 13-24, or 25-36 |
| Even Money | 1:1 | Red/Black, Odd/Even, 1-18/19-36 |

### Call Bets (Announced Bets)

| Bet | Description |
|-----|-------------|
| Voisins du Zéro | 17 numbers surrounding zero on the wheel |
| Tiers du Cylindre | 12 numbers opposite zero on the wheel |
| Orphelins | 8 numbers not in Voisins or Tiers |
| Jeu Zéro | 7 numbers closest to zero |

## Getting Started

1. Install `uv` if you don't have it:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install and run:
   ```bash
   uv pip install -e .
   uv run justai-roulette
   ```

### Optional: Enable Audio

For cross-platform sound effects:
```bash
uv pip install -e ".[audio]"
```

## Controls

- **Click table** - Place bet on number, split, corner, or outside bet
- **Click chip** - Select chip denomination ($0.50 - $50)
- **Quick Bet buttons** - One-touch outside bets
- **SPIN** - Spin the wheel
- **Re-bet** - Repeat previous spin's bets
- **Double** - Double all current bets
- **Undo** - Remove last bet
- **Clear** - Remove all bets
- **Type 0-36** - Quick number bet via keyboard

## Keyboard Shortcuts

- Type numbers 0-36 to quickly bet on that number
- Numbers are buffered for 700ms to allow typing two-digit numbers

## Project Layout

```
justai-roulette/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # This file
└── src/justai_roulette/
    ├── __init__.py
    ├── __main__.py             # Main application entry point
    ├── constants.py            # Colors, wheel sequence, chip values
    ├── audio.py                # Cross-platform sound effects
    ├── session.py              # Session persistence
    ├── game/
    │   ├── __init__.py
    │   └── bets.py             # Bet definitions and payouts
    └── ui/
        ├── __init__.py
        ├── wheel.py            # Wheel visualization component
        ├── table.py            # Betting table component
        ├── controls.py         # Quick bet and action buttons
        └── theme.py            # ttk styling and themes
```

## Configuration

Session data is saved to `~/.justai_roulette_session.json` including:
- Current balance
- Spin history (last 50)
- Hot/cold number statistics
- Color and parity distribution
- Auto-spin settings
- Sound preferences

## Requirements

- Python 3.8+
- Tkinter (usually included with Python)
- Optional: simpleaudio, numpy (for cross-platform audio)

## License

MIT
