"""Roulette betting table component."""

from tkinter import Canvas, BOTH
from typing import Callable

from ..constants import Colors, RED_NUMBERS, TABLE_ROWS, COLUMNS

_DOZENS = {
    "1st 12 (1-12)": list(range(1, 13)),
    "2nd 12 (13-24)": list(range(13, 25)),
    "3rd 12 (25-36)": list(range(25, 37)),
}


def _number_color(n: int) -> tuple[str, str]:
    if n == 0:
        return Colors.GREEN, "white"
    return (Colors.RED if n in RED_NUMBERS else Colors.BLACK), "white"


def build_table(parent, on_select: Callable) -> tuple:
    """Create a roulette table grid on a Canvas with clickable bets."""
    cell_w, cell_h = 60, 44
    zero_w = 78
    edge_tol = 8
    col_box_w = 72
    extra_h = 44

    rows = TABLE_ROWS
    width_numbers = zero_w + len(rows[0]) * cell_w
    padding_x, padding_y = 8, 6
    width = padding_x * 2 + width_numbers + col_box_w
    height = padding_y * 2 + len(rows) * cell_h + extra_h * 2

    canvas = Canvas(parent, width=width, height=height, bg=Colors.FELT, highlightthickness=0)
    canvas.pack(padx=12, pady=(4, 16), fill=BOTH, expand=True)

    scale_state = {"factor": 1.0, "offset": (0.0, 0.0)}
    markers: dict[tuple[int, ...], dict] = {}
    number_centers: dict[int, tuple[float, float]] = {}
    outside_bet_centers: dict[str, tuple[float, float]] = {}

    def _cell_bbox(r, c):
        x0 = padding_x + zero_w + c * cell_w
        y0 = padding_y + r * cell_h
        return x0, y0, x0 + cell_w, y0 + cell_h

    def _zero_bbox():
        return padding_x, padding_y, padding_x + zero_w, padding_y + len(rows) * cell_h

    def _draw_cells():
        """Draw table cells once at startup."""
        # Zero
        zx0, zy0, zx1, zy1 = _zero_bbox()
        bg, fg = _number_color(0)
        canvas.create_rectangle(zx0, zy0, zx1, zy1, fill=bg, outline="white", width=2)
        number_centers[0] = ((zx0 + zx1) / 2, (zy0 + zy1) / 2)
        canvas.create_text((zx0 + zx1) / 2, (zy0 + zy1) / 2, text="0", fill=fg, font=("Segoe UI", 20, "bold"))

        # Numbers
        for r, row_data in enumerate(rows):
            for c, num in enumerate(row_data):
                x0, y0, x1, y1 = _cell_bbox(r, c)
                bg, fg = _number_color(num)
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                number_centers[num] = (cx, cy)
                canvas.create_rectangle(x0, y0, x1, y1, fill=bg, outline="white")
                canvas.create_text(cx, cy, text=str(num), fill=fg, font=("Segoe UI", 16, "bold"))

        # Column boxes
        col_x0 = padding_x + width_numbers
        col_x1 = col_x0 + col_box_w
        for i, name in enumerate(["Col 3", "Col 2", "Col 1"]):
            y0, y1 = padding_y + i * cell_h, padding_y + (i + 1) * cell_h
            canvas.create_rectangle(col_x0, y0, col_x1, y1, fill="#145a32", outline="white")
            canvas.create_text((col_x0 + col_x1) / 2, (y0 + y1) / 2, text="2:1", fill="white", font=("Segoe UI", 16, "bold"))
            outside_bet_centers[name] = ((col_x0 + col_x1) / 2, (y0 + y1) / 2)

        # Dozens
        dozen_y0 = padding_y + len(rows) * cell_h
        dozen_y1 = dozen_y0 + extra_h
        box_w = (width_numbers - zero_w) / 3
        for i, (label, name) in enumerate(zip(_DOZENS.keys(), ["1st 12", "2nd 12", "3rd 12"])):
            x0, x1 = padding_x + zero_w + i * box_w, padding_x + zero_w + (i + 1) * box_w
            canvas.create_rectangle(x0, dozen_y0, x1, dozen_y1, fill="#0f7a3a", outline="white")
            canvas.create_text((x0 + x1) / 2, (dozen_y0 + dozen_y1) / 2, text=label, fill="white", font=("Segoe UI", 15, "bold"))
            outside_bet_centers[name] = ((x0 + x1) / 2, (dozen_y0 + dozen_y1) / 2)

        # Outside bets
        outside_y0, outside_y1 = dozen_y1, dozen_y1 + extra_h
        box_w_out = (width_numbers - zero_w) / 6
        for i, label in enumerate(["1-18", "Even", "Red", "Black", "Odd", "19-36"]):
            x0, x1 = padding_x + zero_w + i * box_w_out, padding_x + zero_w + (i + 1) * box_w_out
            bg = Colors.RED if label == "Red" else Colors.BLACK if label == "Black" else "#0b6b33"
            canvas.create_rectangle(x0, outside_y0, x1, outside_y1, fill=bg, outline="white")
            canvas.create_text((x0 + x1) / 2, (outside_y0 + outside_y1) / 2, text=label, fill="white", font=("Segoe UI", 15, "bold"))
            outside_bet_centers[label] = ((x0 + x1) / 2, (outside_y0 + outside_y1) / 2)

    def _scale_point(x, y, radius=None):
        """Convert logical coords to screen coords."""
        sf = scale_state["factor"] or 1.0
        ox, oy = scale_state["offset"]
        sx, sy = ox + x * sf, oy + y * sf
        return (sx, sy) if radius is None else (sx, sy, max(6.0, radius * sf))

    def _apply_scale(new_w, new_h):
        """Scale canvas using canvas.scale() - no redraw needed."""
        if new_w < 10 or new_h < 10:
            return
        new_factor = min(new_w / width, new_h / height, 2.3)
        if new_factor <= 0:
            return
        draw_w, draw_h = width * new_factor, height * new_factor
        ox, oy = (new_w - draw_w) / 2, (new_h - draw_h) / 2
        prev_factor = scale_state["factor"] or 1.0
        delta = new_factor / prev_factor
        if abs(delta - 1) < 0.02 and abs(ox - scale_state["offset"][0]) < 2 and abs(oy - scale_state["offset"][1]) < 2:
            return
        # Scale ALL items in place - no redraw
        canvas.scale("all", 0, 0, delta, delta)
        canvas.move("all", ox - scale_state["offset"][0], oy - scale_state["offset"][1])
        scale_state["factor"] = new_factor
        scale_state["offset"] = (ox, oy)

    def _get_outside_numbers(label):
        if label == "1-18": return list(range(1, 19))
        if label == "19-36": return list(range(19, 37))
        if label == "Even": return [n for n in range(1, 37) if n % 2 == 0]
        if label == "Odd": return [n for n in range(1, 37) if n % 2 == 1]
        if label == "Red": return [n for n in range(1, 37) if n in RED_NUMBERS]
        if label == "Black": return [n for n in range(1, 37) if n not in RED_NUMBERS]
        return []

    def _detect_bet(raw_x, raw_y):
        """Detect what bet was clicked."""
        sf = scale_state["factor"] or 1.0
        ox, oy = scale_state["offset"]
        x, y = (raw_x - ox) / sf, (raw_y - oy) / sf

        zx0, zy0, zx1, zy1 = _zero_bbox()
        dozen_y0, dozen_y1 = zy1, zy1 + extra_h
        outside_y0, outside_y1 = dozen_y1, dozen_y1 + extra_h
        col_x0, col_x1 = padding_x + width_numbers, padding_x + width_numbers + col_box_w

        # Zero
        if zx0 <= x <= zx1 and zy0 <= y <= zy1:
            return "Straight 0", [0], 35, (zx0 + zx1) / 2, (zy0 + zy1) / 2

        # Columns
        if col_x0 <= x <= col_x1 and zy0 <= y <= zy1:
            idx = int((y - zy0) // cell_h)
            if 0 <= idx < 3:
                col_map = {0: ("Column 3", COLUMNS[2]), 1: ("Column 2", COLUMNS[1]), 2: ("Column 1", COLUMNS[0])}
                label, nums = col_map[idx]
                return label, nums, 2, (col_x0 + col_x1) / 2, zy0 + idx * cell_h + cell_h / 2

        # Dozens
        if dozen_y0 <= y <= dozen_y1:
            x_off = x - (padding_x + zero_w)
            if 0 <= x_off <= width_numbers - zero_w:
                segment_w = (width_numbers - zero_w) / 3
                idx = int(x_off // segment_w)
                if 0 <= idx < 3:
                    labels = list(_DOZENS.keys())
                    return labels[idx], _DOZENS[labels[idx]], 2, x, (dozen_y0 + dozen_y1) / 2

        # Outside bets
        if outside_y0 <= y <= outside_y1:
            x_off = x - (padding_x + zero_w)
            if 0 <= x_off <= width_numbers - zero_w:
                labels = ["1-18", "Even", "Red", "Black", "Odd", "19-36"]
                segment_w = (width_numbers - zero_w) / 6
                idx = int(x_off // segment_w)
                if 0 <= idx < 6:
                    return labels[idx], _get_outside_numbers(labels[idx]), 1, x, (outside_y0 + outside_y1) / 2

        # Outside table
        if x < zx1 or x > col_x1 or y < zy0 or y > outside_y1:
            return None

        # Number grid
        col = int((x - zx1) // cell_w)
        row = int((y - zy0) // cell_h)
        if not (0 <= row < len(rows) and 0 <= col < len(rows[0])):
            return None

        num = rows[row][col]
        x0, y0, x1, y1 = _cell_bbox(row, col)
        lx, ly = x - x0, y - y0

        def nb(ro, co):
            nr, nc = row + ro, col + co
            return rows[nr][nc] if 0 <= nr < len(rows) and 0 <= nc < len(rows[0]) else None

        nl, nr, nt, nb_ = lx <= edge_tol, lx >= cell_w - edge_tol, ly <= edge_tol, ly >= cell_h - edge_tol

        # Corners
        if nl and nt and (n := nb(-1, -1)): return "Corner", [num, nb(-1, 0), nb(0, -1), n], 8, x0, y0
        if nr and nt and (n := nb(-1, 1)): return "Corner", [num, nb(-1, 0), nb(0, 1), n], 8, x1, y0
        if nl and nb_ and (n := nb(1, -1)): return "Corner", [num, nb(0, -1), nb(1, 0), n], 8, x0, y1
        if nr and nb_ and (n := nb(1, 1)): return "Corner", [num, nb(1, 0), nb(0, 1), n], 8, x1, y1

        # Splits
        if nl and (n := nb(0, -1)): return f"Split {num}/{n}", [num, n], 17, x0, (y0 + y1) / 2
        if nr and (n := nb(0, 1)): return f"Split {num}/{n}", [num, n], 17, x1, (y0 + y1) / 2
        if nt and (n := nb(-1, 0)): return f"Split {num}/{n}", [num, n], 17, (x0 + x1) / 2, y0
        if nb_ and (n := nb(1, 0)): return f"Split {num}/{n}", [num, n], 17, (x0 + x1) / 2, y1

        return f"Straight {num}", [num], 35, (x0 + x1) / 2, (y0 + y1) / 2

    def _update_marker(key, amount, x, y):
        """Update marker in place using itemconfigure - NO redraw."""
        if key in markers:
            # Just update the text - don't delete/recreate
            canvas.itemconfigure(markers[key]["text_id"], text=str(int(amount) if amount == int(amount) else amount))
        else:
            # Create new marker
            r = 10.0
            sx, sy, sr = _scale_point(x, y, r)
            oval_id = canvas.create_oval(sx - sr, sy - sr, sx + sr, sy + sr, fill="#f1c40f", outline="#c27c0e", width=2)
            text_id = canvas.create_text(sx, sy, text=str(int(amount) if amount == int(amount) else amount), font=("Segoe UI", 9, "bold"), fill="black")
            markers[key] = {"oval_id": oval_id, "text_id": text_id, "x": x, "y": y}

    def _clear_markers():
        for data in markers.values():
            canvas.delete(data.get("oval_id"))
            canvas.delete(data.get("text_id"))
        markers.clear()

    def _on_click(event):
        bet = _detect_bet(event.x, event.y)
        if bet:
            label, nums, payout, cx, cy = bet
            on_select(label, nums, payout, tuple(sorted(nums)), cx, cy, _update_marker)

    # Draw table once, bind click, set up scaling
    _draw_cells()
    canvas.bind("<ButtonPress-1>", _on_click)
    canvas.bind("<Configure>", lambda e: _apply_scale(e.width, e.height))

    return (_clear_markers, _update_marker, number_centers, outside_bet_centers, canvas, _scale_point)
