"""Constants and configuration for JustAI Roulette."""

from pathlib import Path

# Roulette numbers
RED_NUMBERS = frozenset({1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36})

CHIP_VALUES = (0.5, 1, 5, 10, 20, 50)

# Table layout rows (top to bottom)
TABLE_ROWS = [
    [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
]

COLUMNS = [
    [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],  # Column 1 (bottom row)
    [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],  # Column 2 (middle row)
    [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],  # Column 3 (top row)
]

# European wheel order starting at zero and going clockwise
WHEEL_SEQUENCE = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
    5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26,
]

# RSL Club Machine Color Scheme
class Colors:
    BG = "#1a0a10"              # Deep burgundy-black background
    CARD_BG = "#2d1520"         # Rich burgundy card background
    ACCENT = "#ffd700"          # Bright gold accent
    ACCENT_DIM = "#b8860b"      # Dark goldenrod for borders
    FELT = "#006633"            # Classic casino green
    WHEEL_RING = "#3d1f2a"      # Burgundy wheel hub
    TEXT_LIGHT = "#fff8e7"      # Warm white text
    TEXT_MUTED = "#c9a0a0"      # Muted rose for secondary text
    BORDER = "#5c3040"          # Burgundy border
    BUTTON_BG = "#4a1c2c"       # RSL burgundy button
    BUTTON_ACTIVE = "#6b2840"   # Active button burgundy
    BUTTON_HOVER = "#7a3350"    # Hover state
    CHROME = "#c0c0c0"          # Chrome/silver for bezels
    CHROME_DARK = "#808080"     # Dark chrome
    LED_GLOW = "#ff6b6b"        # LED red glow
    WIN_FLASH = "#ffd700"       # Gold flash for wins
    RED = "#c0392b"             # Roulette red
    BLACK = "#1c1c1c"           # Roulette black
    GREEN = "#0ecf6e"           # Roulette green (zero)
    # Wood colors for table border
    WOOD_DARK = "#4a2c17"       # Dark mahogany
    WOOD_MID = "#6b3d22"        # Medium wood
    WOOD_LIGHT = "#8b5a2b"      # Light wood highlight
    WOOD_GRAIN = "#3d2212"      # Wood grain lines

# Session and limits
SESSION_FILE = Path.home() / ".justai_roulette_session.json"
MAX_SINGLE_BET = 100.0
DEFAULT_BALANCE = 100.0

# Chip colors for display
CHIP_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#9b59b6", "#f39c12", "#1abc9c"]
