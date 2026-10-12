"""Elytra: the worn wings (``entity/equipment/wings/elytra.png``) and the two inventory icons.

The wing model is a 10 x 20 x 2 box at ``texOffs(22, 0)`` (``uv.box_faces``), and only its *outer* face
(36..45, 2..21) is visible: the game renders it unculled, so from the inside you see the same
sheet from behind.  Like vanilla, only that face is painted.  The wing is a rectangle with two
diagonal corners cut off (top, towards the neck, and bottom, towards the wing tip) so it reads as
a wing instead of a plank; the right wing reuses the patch mirrored, so the design is symmetrical.

Look: navy membrane with pleats, a glowing cyan edge, and a small cyan gem at the shoulder.
"""
from __future__ import annotations

from .. import theme
from ..sprite import Sprite, mix
from ..uv import box_faces
from .items import _cells, shade_part

NAVY = theme.NAVY
CLASP = ("#eef2f7", "#b4bdcb", "#b4bdcb", "#7a8496")        # 2x2 silver clasp: lit facet, two mid facets, shadow

EQUIP = "assets/minecraft/textures/entity/equipment/wings"
ITEM = "assets/minecraft/textures/item"

WING = box_faces(22, 0, 10, 20, 2)["back"]       # (36, 2, 10, 20): the visible face
assert WING == (36, 2, 10, 20)


def _wing_cells() -> set:
    """Pixels of the outer face that belong to the wing: the rectangle minus two 45-degree corner cuts."""
    x0, y0, w, h = WING
    cells = set()
    for ly in range(h):
        for lx in range(w):
            if lx - ly >= 6:                         # top-right, towards the neck
                continue
            if lx + (h - 1 - ly) < 3:                # bottom-left, the wing tip
                continue
            cells.add((x0 + lx, y0 + ly))
    return cells


def wing_texture() -> Sprite:
    s = Sprite(64, 32)
    cells = _wing_cells()
    x0, y0, w, h = WING
    for (x, y) in cells:
        lx, ly = x - x0, y - y0
        edge = any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            c = theme.ACCENT_DARK if (x + y) % 3 else theme.ACCENT                  # glowing rim
        else:
            base = NAVY.m if ly < h * 0.55 else mix(NAVY.m, NAVY.d, 0.5)           # darker towards the tip
            if lx in (2, 5, 8):                                                      # pleats
                c = NAVY.d
            elif lx in (3, 6, 9):
                c = NAVY.l if ly % 4 == 0 else base
            else:
                c = base
            if ly % 6 == 5:
                c = mix(c, NAVY.d, 0.35)                                             # feather joints
        s.set(x, y, c)
    # silver clasp (2x2) near the pivot corner
    for (dx, dy), c in zip(((0, 0), (1, 0), (0, 1), (1, 1)), CLASP):
        s.set(x0 + 1 + dx, y0 + 2 + dy, c)
    return s


# --------------------------------------------------------------------------- icons
HALF = [        # right half of the icon (x = 8..15); the left half is the mirror image
    "........",
    "........",
    ".M......",
    ".MMM....",
    ".MMMMM..",
    ".MMMMMM.",
    ".MMMMMM.",
    "..MMMMMM",
    "..MMMMMM",
    "...MMMMM",
    "...MMMM.",
    "....MMM.",
    "....MM..",
    ".....M..",
    "........",
    "........",
]


def _icon_cells() -> set:
    right = {(8 + x, y) for (x, y) in _cells(HALF)}
    return right | {(15 - x, y) for (x, y) in right}


def elytra_icon(broken: bool = False) -> Sprite:
    cells = _icon_cells()
    if broken:
        cells -= {(12, 8), (12, 9), (13, 9), (3, 6), (3, 7), (2, 7), (10, 12), (5, 11), (5, 12), (13, 5), (2, 4)}
    s = Sprite(16, 16)
    for (x, y) in cells:
        c = shade_part(x, y, cells, NAVY)
        edge_top = (x, y - 1) not in cells
        outer = (x + 1, y) not in cells if x >= 8 else (x - 1, y) not in cells
        if edge_top or outer:
            c = theme.ACCENT_DARK if not broken else mix(theme.ACCENT_DARK, "#555b66", 0.6)
        if broken:
            c = mix(c, "#6b7078", 0.35)
        s.set(x, y, c)
    for y in range(4, 11):                                       # spine / pleat lines
        for x in (10, 5):
            if (x, y) in cells and (y - 4) % 3 == 1:
                s.set(x, y, NAVY.d)
    if not broken:
        for (dx, dy), c in zip(((0, 0), (1, 0), (0, 1), (1, 1)), CLASP):
            s.set(7 + dx, 3 + dy, c)
    s.outline(theme.INK)
    return s


def generate(pack) -> None:
    pack.png(f"{EQUIP}/elytra.png", wing_texture())
    pack.png(f"{ITEM}/elytra.png", elytra_icon())
    pack.png(f"{ITEM}/elytra_broken.png", elytra_icon(broken=True))
