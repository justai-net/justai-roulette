"""Bet definitions and payout logic for roulette."""

from ..constants import RED_NUMBERS, COLUMNS

# Quick bet definitions for RSL-style one-touch betting
# Format: (numbers, payout)
QUICK_BETS = {
    "Red": ([n for n in range(1, 37) if n in RED_NUMBERS], 1),
    "Black": ([n for n in range(1, 37) if n not in RED_NUMBERS], 1),
    "Odd": ([n for n in range(1, 37) if n % 2 == 1], 1),
    "Even": ([n for n in range(1, 37) if n % 2 == 0], 1),
    "1-18": (list(range(1, 19)), 1),
    "19-36": (list(range(19, 37)), 1),
    "1st 12": (list(range(1, 13)), 2),
    "2nd 12": (list(range(13, 25)), 2),
    "3rd 12": (list(range(25, 37)), 2),
    "Col 1": (COLUMNS[0], 2),
    "Col 2": (COLUMNS[1], 2),
    "Col 3": (COLUMNS[2], 2),
}

# European call bets - each is a list of (numbers, payout, chip_count) tuples
CALL_BETS = {
    # Voisins du Zéro - 9 chips covering 17 numbers
    "Voisins": [
        ([0, 2, 3], 11, 2),        # 0/2/3 trio - 2 chips
        ([4, 7], 17, 1),           # 4/7 split
        ([12, 15], 17, 1),         # 12/15 split
        ([18, 21], 17, 1),         # 18/21 split
        ([19, 22], 17, 1),         # 19/22 split
        ([25, 26, 28, 29], 8, 2),  # 25/26/28/29 corner - 2 chips
        ([32, 35], 17, 1),         # 32/35 split
    ],
    # Tiers du Cylindre - 6 chips covering 12 numbers
    "Tiers": [
        ([5, 8], 17, 1),
        ([10, 11], 17, 1),
        ([13, 16], 17, 1),
        ([23, 24], 17, 1),
        ([27, 30], 17, 1),
        ([33, 36], 17, 1),
    ],
    # Orphelins - 5 chips covering 8 numbers
    "Orphelins": [
        ([1], 35, 1),              # 1 straight
        ([6, 9], 17, 1),           # 6/9 split
        ([14, 17], 17, 1),         # 14/17 split
        ([17, 20], 17, 1),         # 17/20 split
        ([31, 34], 17, 1),         # 31/34 split
    ],
    # Jeu Zéro - 4 chips covering 7 numbers
    "Jeu Zéro": [
        ([0, 3], 17, 1),           # 0/3 split
        ([12, 15], 17, 1),         # 12/15 split
        ([26], 35, 1),             # 26 straight
        ([32, 35], 17, 1),         # 32/35 split
    ],
    # Snake - 12 chips on straight numbers in zigzag pattern
    "Snake": [
        ([1], 35, 1), ([5], 35, 1), ([9], 35, 1), ([12], 35, 1),
        ([14], 35, 1), ([16], 35, 1), ([19], 35, 1), ([23], 35, 1),
        ([27], 35, 1), ([30], 35, 1), ([32], 35, 1), ([34], 35, 1),
    ],
}


def get_number_color(num: int) -> str:
    """Return 'red', 'black', or 'green' for a roulette number."""
    if num == 0:
        return "green"
    return "red" if num in RED_NUMBERS else "black"


def calculate_winnings(bets: list[dict], winning_number: int) -> tuple[float, list[dict]]:
    """
    Calculate total winnings from placed bets.

    Args:
        bets: List of bet dicts with 'numbers', 'payout', 'amount' keys
        winning_number: The winning roulette number

    Returns:
        Tuple of (total_winnings, list_of_winning_bets)
    """
    total = 0.0
    winners = []

    for bet in bets:
        if winning_number in bet["numbers"]:
            win_amount = bet["amount"] * (bet["payout"] + 1)
            total += win_amount
            winners.append({**bet, "win_amount": win_amount})

    return total, winners
