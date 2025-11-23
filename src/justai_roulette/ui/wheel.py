"""Roulette wheel visualization component."""

import math
from tkinter import Canvas

from ..constants import Colors, RED_NUMBERS, WHEEL_SEQUENCE


def _number_color(n: int) -> tuple[str, str]:
    """Return (bg, fg) colors for a roulette number."""
    if n == 0:
        return Colors.GREEN, "white"
    bg = Colors.RED if n in RED_NUMBERS else Colors.BLACK
    return bg, "white"


def build_wheel(parent) -> dict:
    """
    Create a premium RSL-style wheel visualization with chrome bezels.

    Returns a dict with:
        - canvas: The Canvas widget
        - move_ball: Function to move ball to angle
        - show_result: Function to display winning number
        - reset: Function to reset ball position
        - number_to_angle: Dict mapping numbers to angles
        - cx, cy: Center coordinates
    """
    size = 380
    cx = cy = size // 2
    outer_r = 152
    inner_r = 96
    text_r = 124
    ball_r = 11
    ball_ring_r = (outer_r + inner_r) / 2
    ball_track_r = outer_r + 10

    canvas = Canvas(parent, width=size, height=size, bg=Colors.FELT, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    scale_state = {"factor": 1.0, "offset": (0.0, 0.0)}

    # Outer chrome bezel
    canvas.create_oval(
        cx - outer_r - 24, cy - outer_r - 24,
        cx + outer_r + 24, cy + outer_r + 24,
        fill=Colors.CHROME_DARK, outline=Colors.CHROME, width=4,
    )

    # Ball track ring
    canvas.create_oval(
        cx - ball_track_r - 4, cy - ball_track_r - 4,
        cx + ball_track_r + 4, cy + ball_track_r + 4,
        fill="#1a1a1a", outline=Colors.CHROME_DARK, width=2,
    )

    # Felt ring with gold trim
    canvas.create_oval(
        cx - outer_r - 6, cy - outer_r - 6,
        cx + outer_r + 6, cy + outer_r + 6,
        fill=Colors.FELT, outline=Colors.ACCENT, width=3,
    )

    # Draw wheel segments
    angle_rad_step = 2 * math.pi / len(WHEEL_SEQUENCE)
    number_to_angle: dict[int, float] = {}
    base_angle = -math.pi / 2  # 12 o'clock

    for idx, num in enumerate(WHEEL_SEQUENCE):
        start_rad = base_angle + idx * angle_rad_step
        end_rad = start_rad + angle_rad_step
        mid_rad = start_rad + angle_rad_step / 2
        number_to_angle[num] = mid_rad
        bg, fg = _number_color(num)

        # Ring wedge
        points = [
            cx + outer_r * math.cos(start_rad), cy + outer_r * math.sin(start_rad),
            cx + outer_r * math.cos(end_rad), cy + outer_r * math.sin(end_rad),
            cx + inner_r * math.cos(end_rad), cy + inner_r * math.sin(end_rad),
            cx + inner_r * math.cos(start_rad), cy + inner_r * math.sin(start_rad),
        ]
        canvas.create_polygon(points, fill=bg, outline=Colors.BORDER, width=1)

        tx = cx + text_r * math.cos(mid_rad)
        ty = cy + text_r * math.sin(mid_rad)
        canvas.create_text(tx, ty, text=str(num), fill=fg, font=("Segoe UI", 11, "bold"))

    # Inner hub
    canvas.create_oval(
        cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r,
        fill=Colors.WHEEL_RING, outline=Colors.CHROME, width=3,
    )

    # Decorative inner ring
    canvas.create_oval(
        cx - inner_r + 10, cy - inner_r + 10,
        cx + inner_r - 10, cy + inner_r - 10,
        fill="", outline=Colors.ACCENT_DIM, width=1,
    )

    # Gold pointer
    pointer_base_y = cy - outer_r - 26
    canvas.create_polygon(
        cx - 14, pointer_base_y,
        cx + 14, pointer_base_y,
        cx, cy - outer_r - 2,
        fill=Colors.ACCENT, outline=Colors.CHROME, width=2,
    )
    canvas.create_polygon(
        cx - 7, pointer_base_y + 5,
        cx + 7, pointer_base_y + 5,
        cx, cy - outer_r,
        fill="#ffec80", outline="",
    )

    # Metallic ball
    ball = canvas.create_oval(
        cx - ball_r, cy - ball_ring_r - ball_r,
        cx + ball_r, cy - ball_ring_r + ball_r,
        fill="#e8e8e8", outline="#a0a0a0", width=2,
    )
    ball_highlight = canvas.create_oval(
        cx - ball_r + 2, cy - ball_ring_r - ball_r + 2,
        cx - ball_r + 5, cy - ball_ring_r - ball_r + 5,
        fill="white", outline="",
    )

    # Center LED display
    canvas.create_oval(
        cx - 40, cy - 28, cx + 40, cy + 28,
        fill="#0a0a0a", outline=Colors.CHROME_DARK, width=2,
    )
    center_text = canvas.create_text(cx, cy, text="--", fill=Colors.ACCENT, font=("Courier", 26, "bold"))

    def _apply_scale(new_w: int, new_h: int) -> None:
        if new_w < 10 or new_h < 10:
            return
        new_factor = min(new_w / size, new_h / size, 2.0)
        if new_factor <= 0:
            return
        draw_w = size * new_factor
        draw_h = size * new_factor
        ox = (new_w - draw_w) / 2
        oy = (new_h - draw_h) / 2
        prev_factor = scale_state["factor"] or 1.0
        delta = new_factor / prev_factor
        if abs(delta - 1) < 0.02 and abs(ox - scale_state["offset"][0]) < 2 and abs(oy - scale_state["offset"][1]) < 2:
            return
        canvas.scale("all", 0, 0, delta, delta)
        canvas.move("all", ox - scale_state["offset"][0], oy - scale_state["offset"][1])
        scale_state["factor"] = new_factor
        scale_state["offset"] = (ox, oy)

    canvas.bind("<Configure>", lambda e: _apply_scale(e.width, e.height))

    def move_ball(angle: float, radius: float | None = None, on_track: bool = False):
        r = radius if radius is not None else (ball_track_r if on_track else ball_ring_r)
        sf = scale_state["factor"]
        ox, oy = scale_state["offset"]
        bx = cx + r * math.cos(angle)
        by = cy + r * math.sin(angle)
        sr = ball_r * sf
        canvas.coords(ball, ox + bx * sf - sr, oy + by * sf - sr, ox + bx * sf + sr, oy + by * sf + sr)
        highlight_offset = 3 * sf
        canvas.coords(
            ball_highlight,
            ox + bx * sf - sr + highlight_offset, oy + by * sf - sr + highlight_offset,
            ox + bx * sf - sr + highlight_offset + 4 * sf, oy + by * sf - sr + highlight_offset + 4 * sf,
        )

    def show_result(num: int, color: str):
        if color == "green":
            display_color = "#00ff00"
        elif color == "red":
            display_color = "#ff3333"
        else:
            display_color = Colors.ACCENT
        canvas.itemconfigure(center_text, text=str(num), fill=display_color, font=("Courier", 32, "bold"))

    def reset_ball():
        move_ball(-math.pi / 2, on_track=True)
        canvas.itemconfigure(center_text, text="--", fill=Colors.ACCENT, font=("Courier", 26, "bold"))

    return {
        "canvas": canvas,
        "move_ball": move_ball,
        "show_result": show_result,
        "reset": reset_ball,
        "number_to_angle": number_to_angle,
        "outer_radius": ball_ring_r,
        "ball_track_radius": ball_track_r,
        "cx": cx,
        "cy": cy,
        "ball_radius": ball_r,
    }
