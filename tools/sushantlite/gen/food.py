"""Food icons -- the things you eat mid-fight.

Raw and cooked variants share one silhouette (ASCII mask) and differ in palette and surface detail:
raw meat gets pale fat marbling, cooked meat gets a browned fat rim and grill marks.  Every icon uses
the same light-from-the-top-left bevel and blue-black outline as the tools and armour.

Mask legend    M  meat / body       B  bone       L  leaf (carrots)       E  eye (fish)
Golden apples, the enchanted apple and the totem live in ``items.py``.
"""
from __future__ import annotations

from .. import theme
from ..sprite import Sprite, mix
from ..theme import GREEN, ORANGE, RED, Ramp
from .items import _cells, shade_part

ITEM = "assets/minecraft/textures/item"

# --------------------------------------------------------------------------- masks (16x16)
STEAK = [
    "................",
    "................",
    "....MMMMMMM.....",
    "..MMMMMMMMMMM...",
    ".MMMMMMMMMMMMM..",
    ".MMMMMMMMMMMMMM.",
    "MMMMMMMMMMMMMMM.",
    "MMMMMMMMMMMMMMM.",
    "MMMMMMMMMMMMMM..",
    ".MMMMMMMMMMMMM..",
    "..MMMMMMMMMMM...",
    "...MMMMMMMMM....",
    ".....MMMMM......",
    "................",
    "................",
    "................",
]

PORKCHOP = [
    "................",
    "................",
    ".......MMMMM....",
    ".....MMMMMMMMM..",
    "....MMMMMMMMMMM.",
    "....MMMMMMMMMMM.",
    "....MMMMMMMMMMM.",
    "....MMMMMMMMMM..",
    ".....MMMMMMMMM..",
    "..BB..MMMMMMM...",
    ".BBBB..MMMM.....",
    ".BBBB...........",
    "..BB............",
    "................",
    "................",
    "................",
]

MUTTON = [      # a longer, leaner chop with the bone to the right
    "................",
    "................",
    "...MMMMM........",
    "..MMMMMMMM......",
    ".MMMMMMMMMM.....",
    ".MMMMMMMMMMM....",
    ".MMMMMMMMMMM....",
    ".MMMMMMMMMMMBB..",
    "..MMMMMMMMMBBBB.",
    "...MMMMMMM.BBBB.",
    "....MMMMM...BB..",
    "................",
    "................",
    "................",
    "................",
    "................",
]

DRUMSTICK = [
    "................",
    "................",
    "........MMMMM...",
    "......MMMMMMMM..",
    ".....MMMMMMMMMM.",
    ".....MMMMMMMMMM.",
    ".....MMMMMMMMMM.",
    "......MMMMMMMM..",
    ".....BBMMMMMM...",
    "....BB..MMM.....",
    "...BB...........",
    "..BB............",
    ".BBBB...........",
    ".BBBB...........",
    "................",
    "................",
]

BREAD = [
    "................",
    "................",
    "................",
    "......MMMMMM....",
    "....MMMMMMMMMM..",
    "..MMMMMMMMMMMMM.",
    ".MMMMMMMMMMMMMMM",
    ".MMMMMMMMMMMMMMM",
    ".MMMMMMMMMMMMMMM",
    ".MMMMMMMMMMMMMMM",
    "..MMMMMMMMMMMMM.",
    "...MMMMMMMMMMM..",
    "................",
    "................",
    "................",
    "................",
]

POTATO = [
    "................",
    "................",
    "................",
    "......MMMMMM....",
    "....MMMMMMMMMM..",
    "...MMMMMMMMMMMM.",
    "..MMMMMMMMMMMMM.",
    "..MMMMMMMMMMMMM.",
    "..MMMMMMMMMMMMM.",
    "...MMMMMMMMMMM..",
    "....MMMMMMMMM...",
    "......MMMMM.....",
    "................",
    "................",
    "................",
    "................",
]

CARROT = [
    "................",
    "..........L.L...",
    ".........LLLLL..",
    "........LLLLLL..",
    "........MMMLL...",
    ".......MMMMM....",
    "......MMMMMM....",
    ".....MMMMMM.....",
    "....MMMMMM......",
    "...MMMMMM.......",
    "..MMMMM.........",
    ".MMMM...........",
    ".MM.............",
    "................",
    "................",
    "................",
]

FISH = [
    "................",
    "................",
    "................",
    "....MMMM........",
    "..MMMMMMMM..M...",
    ".MMMMMMMMMMMMMM.",
    ".MEMMMMMMMMMMMM.",
    ".MMMMMMMMMMMMMM.",
    "..MMMMMMMM..M...",
    "....MMMM........",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]


# --------------------------------------------------------------------------- shading helpers
def _edges(x: int, y: int, solid: set) -> tuple[bool, bool]:
    lit = (x, y - 1) not in solid or (x - 1, y) not in solid
    dark = (x, y + 1) not in solid or (x + 1, y) not in solid
    return lit, dark


def meat_icon(rows, meat: Ramp, fat: Ramp | None, bone: Ramp | None, cooked: bool) -> Sprite:
    cells = _cells(rows)
    solid = set(cells)
    meat_cells = {p for p, ch in cells.items() if ch == "M"}
    s = Sprite(16, 16)
    for (x, y), ch in cells.items():
        if ch == "B":
            s.set(x, y, shade_part(x, y, solid, bone))
            continue
        lit, dark = _edges(x, y, solid)
        if fat is not None and lit and not dark:
            s.set(x, y, fat.l)                                   # fat rim along the lit edge
        elif fat is not None and lit:
            s.set(x, y, fat.m)
        elif dark and not lit:
            s.set(x, y, meat.d)
        else:
            s.set(x, y, meat.m)
    interior = [(x, y) for (x, y) in meat_cells if all((x + dx, y + dy) in meat_cells for dx, dy in
                                                       ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)))]
    for x, y in interior:
        if cooked:
            if (x - y) % 5 == 0:                                  # grill marks
                s.set(x, y, mix(meat.d, "#1c0a04", 0.55))
            elif (x * 3 + y * 7) % 13 == 0:
                s.set(x, y, meat.l)
        else:
            if (2 * x + 5 * y) % 11 == 0:                         # marbling
                s.set(x, y, meat.s if fat is None else fat.l)
            elif (x * 3 + y * 7) % 9 == 0:
                s.set(x, y, meat.l)
    s.outline(theme.INK)
    return s


def bread() -> Sprite:
    crust = Ramp("#6f411a", "#b87a30", "#dea152", "#f6cf86")
    cells = _cells(BREAD)
    solid = set(cells)
    s = Sprite(16, 16)
    for (x, y) in cells:
        lit, dark = _edges(x, y, solid)
        s.set(x, y, crust.l if lit and not dark else crust.d if dark and not lit else crust.m)
    for x, y in ((4, 9), (5, 10), (11, 10), (10, 11)):           # darker underside
        if (x, y) in solid:
            s.set(x, y, crust.d)
    for x0 in (5, 8, 11):                                         # three scoring cuts
        s.set(x0, 6, crust.s)
        s.set(x0 - 1, 7, crust.l)
        s.set(x0 + 1, 5, crust.l) if (x0 + 1, 5) in solid else None
    s.outline(theme.INK)
    return s


def baked_potato() -> Sprite:
    skin = Ramp("#5e3b18", "#9a6430", "#c58e47", "#e8bb78")
    cells = _cells(POTATO)
    solid = set(cells)
    s = Sprite(16, 16)
    for (x, y) in cells:
        lit, dark = _edges(x, y, solid)
        c = skin.l if lit and not dark else skin.d if dark and not lit else skin.m
        if (x * 7 + y * 3) % 10 == 0:
            c = skin.d                                            # blemishes
        s.set(x, y, c)
    for x in range(6, 11):                                        # the split, with a pat of butter
        s.set(x, 5, "#fff3c4")
        s.set(x, 6, "#e9d79a")
    s.set(7, 5, "#ffd84a")
    s.set(8, 5, "#ffe880")
    s.set(8, 4, "#ffd84a") if (8, 4) in solid else None
    s.outline(theme.INK)
    return s


def carrot(leaf: Ramp, body: Ramp, gold: bool) -> Sprite:
    cells = _cells(CARROT)
    solid = set(cells)
    s = Sprite(16, 16)
    for (x, y), ch in cells.items():
        lit, dark = _edges(x, y, solid)
        if ch == "L":
            s.set(x, y, leaf.l if (x + y) % 2 else leaf.m)
            continue
        c = body.l if lit and not dark else body.d if dark and not lit else body.m
        s.set(x, y, c)
    for (x, y), ch in cells.items():                             # ridges across the root
        if ch == "M" and (x + y) % 4 == 1 and (x - y) % 2 == 0 and (x, y) != (11, 4):
            s.set(x, y, body.d)
    if gold:
        for x, y in ((7, 6), (5, 8)):
            if cells.get((x, y)) == "M":
                s.set(x, y, body.s)
    s.set(8, 4, body.d)
    s.outline(theme.INK)
    return s


def fish(body: Ramp, belly: Ramp, tail: Ramp, cooked: bool) -> Sprite:
    cells = _cells(FISH)
    solid = set(cells)
    s = Sprite(16, 16)
    for (x, y), ch in cells.items():
        if ch == "E":
            s.set(x, y, "#0c1018")
            continue
        lit, dark = _edges(x, y, solid)
        if x >= 12 or (x >= 10 and y in (4, 8)):                  # tail fin
            c = tail.l if lit else tail.m if not dark else tail.d
        elif y >= 7:
            c = belly.m if not dark else belly.d                  # paler belly
        else:
            c = body.l if lit and not dark else body.d if dark and not lit else body.m
        s.set(x, y, c)
    for x in range(4, 11):                                        # gill line + back pattern
        if (x, 4) in solid and x % 2 == 0:
            s.set(x, 4, body.d)
    if cooked:
        for x in range(5, 12, 2):
            s.set(x, 6, mix(body.d, "#2a1008", 0.4))              # grill stripes
    else:
        s.set(4, 5, body.s)
        s.set(9, 5, body.l)
    s.outline(theme.INK)
    return s


def apple() -> Sprite:
    from .items import _disc_cells, shaded
    body = _disc_cells(8, 9.8, 5.6) - {(8, 4), (7, 4)}
    s = shaded(body, RED)
    for x, y in ((5, 7), (6, 6)):
        s.set(x, y, RED.s)
    s.set(5, 8, RED.l)
    for x, y in ((8, 3), (8, 2)):
        s.set(x, y, "#6a4420")
    for x, y in ((9, 2), (10, 2), (10, 3)):
        s.set(x, y, GREEN.m if (x, y) != (10, 3) else GREEN.d)
    s.outline(theme.INK)
    return s


# --------------------------------------------------------------------------- palettes
BEEF_RAW = Ramp("#7a1020", "#b3253a", "#d9475c", "#f2a0ab")
BEEF_COOKED = Ramp("#4a230f", "#7d3d1b", "#a85a2b", "#d08040")
FAT_RAW = Ramp("#cfa9a0", "#ecd0c8", "#fff1ec", "#ffffff")
FAT_COOKED = Ramp("#9a6a3a", "#c58e55", "#e3b27a", "#f6d3a0")
PORK_RAW = Ramp("#c0607a", "#ec8fa5", "#ffb3c4", "#ffd9e2")
PORK_COOKED = Ramp("#8a4a2a", "#c07a4a", "#e6a06b", "#f6c490")
MUTTON_RAW = Ramp("#6a1424", "#a02a40", "#c9475f", "#eea0ae")
MUTTON_COOKED = Ramp("#40240f", "#6e4220", "#966233", "#c28a52")
CHICKEN_RAW = Ramp("#c58b86", "#efb9b0", "#ffd9d0", "#fff0ea")
CHICKEN_COOKED = Ramp("#9a5a1e", "#d28a30", "#f0b04e", "#ffd88a")
BONE = Ramp("#a8a08c", "#d8d1bd", "#f6f1e0", "#ffffff")
SALMON_RAW = Ramp("#9c2f3a", "#d65a5a", "#f08a80", "#ffc6b8")
SALMON_COOKED = Ramp("#9a4a1c", "#d97a38", "#f2a263", "#ffd0a0")
COD_RAW = Ramp("#6f6552", "#a39579", "#cdbf9e", "#ece2c6")
COD_COOKED = Ramp("#8a5a30", "#c48b50", "#e3b378", "#f6d6a2")


def generate(pack) -> None:
    out = {
        "beef": meat_icon(STEAK, BEEF_RAW, FAT_RAW, None, False),
        "cooked_beef": meat_icon(STEAK, BEEF_COOKED, FAT_COOKED, None, True),
        "porkchop": meat_icon(PORKCHOP, PORK_RAW, None, BONE, False),
        "cooked_porkchop": meat_icon(PORKCHOP, PORK_COOKED, None, BONE, True),
        "mutton": meat_icon(MUTTON, MUTTON_RAW, None, BONE, False),
        "cooked_mutton": meat_icon(MUTTON, MUTTON_COOKED, None, BONE, True),
        "chicken": meat_icon(DRUMSTICK, CHICKEN_RAW, None, BONE, False),
        "cooked_chicken": meat_icon(DRUMSTICK, CHICKEN_COOKED, None, BONE, True),
        "bread": bread(),
        "baked_potato": baked_potato(),
        "carrot": carrot(GREEN, ORANGE, False),
        "golden_carrot": carrot(GREEN, theme.GOLD, True),
        "apple": apple(),
        "salmon": fish(SALMON_RAW, Ramp("#e8b0a0", "#f4cfc2", "#fde6dc", "#ffffff"), SALMON_RAW, False),
        "cooked_salmon": fish(SALMON_COOKED, Ramp("#d9a068", "#f0c490", "#fbdcb0", "#fff0d0"), SALMON_COOKED, True),
        "cod": fish(COD_RAW, Ramp("#c9bfa4", "#e4dcc4", "#f4eedb", "#ffffff"), COD_RAW, False),
        "cooked_cod": fish(COD_COOKED, Ramp("#c9a070", "#e3c394", "#f3dcb4", "#fff0d0"), COD_COOKED, True),
    }
    for name, sprite in out.items():
        pack.png(f"{ITEM}/{name}.png", sprite)
