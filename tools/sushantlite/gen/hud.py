"""Clean, high-contrast HUD: hotbar, crosshair, hearts, food, armour, air, XP.

Look: a neutral charcoal bar with a light-grey frame round every slot, a white selection ring with a
cyan inner line, white (not blue) armour icons and round air bubbles.

All sprites keep the exact vanilla dimensions and layout contracts, which the
validator enforces:

* ``hotbar`` is 182x22 with 16x16 item cells at x = 3 + 20*slot, y = 3.
* ``hotbar_selection`` is 24x23 with a transparent 16x16 hole at (4, 4).
* offhand slots are 29x24 with the 16x16 cell at (3, 4) / (10, 4).
* ``heart/full|half`` and ``food_full|half`` are *fill only* sprites drawn over
  their ``container`` / ``food_empty`` sprite, which carries the outline.
* the crosshair is drawn with an inverting blend, so it is pure white.
"""
from __future__ import annotations

from .. import theme
from ..sprite import Sprite, mix, rgba, with_alpha
from ..theme import Ramp

SP = "assets/minecraft/textures/gui/sprites/hud"

INK = "#07080a"
GLASS_TOP = "#4b4d55"
EDGE_OUT = "#9ea1aa"          # the light-grey frame of each slot
EDGE_IN = "#25262b"
INTERIOR = with_alpha(theme.PANEL, theme.PANEL_ALPHA)
SLOT_DARK = "#1d1e23"         # fill of empty heart / food / armour containers


# =============================================================================
# Hotbar
# =============================================================================
def hotbar() -> Sprite:
    s = Sprite(182, 22).fill(with_alpha(INK, 240))
    s.rect(0, 0, 182, 1, GLASS_TOP)
    for k in range(9):
        x0 = 1 + 20 * k
        s.rect(x0, 1, 20, 20, EDGE_OUT)
        s.rect(x0 + 1, 2, 18, 18, EDGE_IN)
        s.rect(x0 + 2, 3, 16, 16, INTERIOR)       # 16x16 item cell at (3 + 20k, 3)
    return s


def selection() -> Sprite:
    """24x23 ring around the selected slot; (4,4)..(19,19) stays transparent for the item."""
    s = Sprite(24, 23)
    ring_cols = [theme.INK, "#f3f6f9", "#f3f6f9", "#8fdff4"]                  # outer -> inner (4 px)
    for i, c in enumerate(ring_cols):            # left / top / right sides are 4 px thick
        s.rect(i, 0, 1, 23, c)
        s.rect(23 - i, 0, 1, 23, c)
    for i, c in enumerate(ring_cols):
        s.rect(0, i, 24, 1, c)
    bottom = [theme.INK, "#f3f6f9", "#8fdff4"]                               # bottom is 3 px thick
    for i, c in enumerate(bottom):
        s.rect(0, 22 - i, 24, 1, c)
    # hollow out the interior (item cell plus the slot frame beneath the ring)
    s.rect(4, 4, 16, 16, None)
    # soften the corners
    for x, y in ((0, 0), (23, 0), (0, 22), (23, 22)):
        s.set(x, y, None)
    return s


def offhand(left: bool) -> Sprite:
    s = Sprite(29, 24)
    x0 = 0 if left else 7
    s.rect(x0, 1, 22, 22, with_alpha(INK, 240))
    s.rect(x0 + 1, 2, 20, 20, EDGE_OUT)
    s.rect(x0 + 2, 3, 18, 18, EDGE_IN)
    s.rect(x0 + 3, 4, 16, 16, INTERIOR)           # item cell at (3,4) left / (10,4) right
    return s


# =============================================================================
# Crosshair + attack indicators
# =============================================================================
def crosshair() -> Sprite:
    s = Sprite(15, 15)
    white = "#ffffff"
    for x, y in ((7, 7), (7, 4), (7, 5), (7, 9), (7, 10), (4, 7), (5, 7), (9, 7), (10, 7)):
        s.set(x, y, white)
    return s


def indicator_full() -> Sprite:
    """Shown when the attack is fully charged: a tiny sword under the crosshair (16x16, art in rows 0..6)."""
    s = Sprite(16, 16)
    s.rect(1, 3, 14, 3, "#ffffff")                    # blade
    s.rect(1, 3, 14, 1, "#dfe5ea")
    s.rect(3, 1, 2, 7, "#9aa0aa")                     # guard
    s.rect(0, 3, 3, 3, "#62666e")                     # pommel
    return s


def indicator_bg() -> Sprite:
    s = Sprite(16, 4).fill(with_alpha(INK, 190))
    s.rect(0, 1, 16, 2, "#2a2b30")
    s.rect(3, 0, 2, 4, "#585b63")
    return s


def indicator_progress() -> Sprite:
    s = Sprite(16, 4)
    s.rect(0, 1, 16, 2, "#ffffff")
    s.rect(0, 1, 16, 1, "#dfe5ea")
    s.rect(3, 0, 2, 4, "#9aa0aa")
    return s


_SWORD18 = [
    "..................",
    "..............OOO.",
    ".............OaaaO",
    "............OaaaO.",
    "...........OaaaO..",
    "..........OaaaO...",
    ".........OaaaO....",
    "........OaaaO.....",
    ".O.....OaaaO......",
    ".OO...OaaaO.......",
    "..OgOOaaaO........",
    "...OgGaaO.........",
    "....OggO..........",
    "...OGgOgO.........",
    "..OGgO.OO.........",
    ".OGgO.............",
    ".OOO..............",
    "..................",
]


def hotbar_indicator(fill: bool) -> Sprite:
    legend_fill = {"O": theme.INK, "a": "#f1f4f7", "g": "#9aa0aa", "G": "#62666e"}
    legend_bg = {"O": with_alpha(theme.PANEL_EDGE, 230), "a": with_alpha(INK, 170),
                 "g": with_alpha(INK, 170), "G": with_alpha(INK, 170)}
    return Sprite.from_ascii(_SWORD18, legend_fill if fill else legend_bg)


# =============================================================================
# Hearts (9x9).  Template: O = outline, f = fill (see shade())
# =============================================================================
HEART = [
    ".OOO.OOO.",
    "OfffOfffO",
    "OfffffffO",
    "OfffffffO",
    "OfffffffO",
    ".OfffffO.",
    "..OfffO..",
    "...OfO...",
    "....O....",
]

HEART_RED = Ramp("#a01428", "#e4263e", "#ff5d73", "#ffd0d6")
HEART_POISON = Ramp("#4b5a10", "#86a22a", "#b4d24b", "#eaf7a6")
HEART_WITHER = Ramp("#0e1013", "#2a2e33", "#484f57", "#8a939c")
HEART_FROZEN = Ramp("#2b6c9c", "#59b4e6", "#a2e0ff", "#f0fbff")
HEART_ABSORB = Ramp("#b9840b", "#f2bc1e", "#ffe059", "#fff5b0")
HEART_VEHICLE = Ramp("#a8480f", "#e57a22", "#ffab55", "#ffe0b4")
STATUS_RAMPS = {"": HEART_RED, "poisoned_": HEART_POISON, "withered_": HEART_WITHER,
                "frozen_": HEART_FROZEN, "absorbing_": HEART_ABSORB}

HEART_FILL = [(x, y) for y, row in enumerate(HEART) for x, ch in enumerate(row) if ch == "f"]
HEART_OUTLINE = [(x, y) for y, row in enumerate(HEART) for x, ch in enumerate(row) if ch == "O"]


def _shade(x: int, y: int) -> str:
    if (x, y) == (2, 1):
        return "s"
    if (x, y) in {(1, 1), (3, 1), (1, 2), (2, 2), (5, 1)}:
        return "l"
    if x + y >= 11 or (x >= 7 and y >= 2):
        return "d"
    return "m"


def heart_fill(ramp: Ramp, half: bool = False, hardcore: bool = False, blink: bool = False) -> Sprite:
    s = Sprite(9, 9)
    for x, y in HEART_FILL:
        if half and x > 4:
            continue
        shade = _shade(x, y)
        c = getattr(ramp, shade)
        if hardcore:                               # deeper, more saturated body with a crisp white glint
            c = "#ffffff" if shade == "s" else mix(c, "#2a0410", 0.30)
        if blink:
            c = mix(c, "#ffffff", 0.62)
        s.set(x, y, c)
    return s


def heart_container(hardcore: bool = False, blink: bool = False, interior=None) -> Sprite:
    s = Sprite(9, 9)
    outline = "#f4fbff" if blink else INK
    inside = interior or ("#474952" if blink else SLOT_DARK)
    if hardcore and not interior:
        inside = "#3c3158" if blink else "#241b36"
    for x, y in HEART_FILL:
        s.set(x, y, inside)
    for x, y in HEART_OUTLINE:
        s.set(x, y, outline)
    # subtle rim light on the top-left of the interior
    if not blink:
        for x, y in ((1, 1), (2, 1), (3, 1), (1, 2)):
            s.set(x, y, mix(inside, "#ffffff", 0.07))
    return s


def hearts(pack) -> None:
    base = f"{SP}/heart"
    for hc in (False, True):
        hp = "hardcore_" if hc else ""
        for blink in (False, True):
            b = "_blinking" if blink else ""
            pack.png(f"{base}/container{'_hardcore' if hc else ''}{b}.png", heart_container(hc, blink))
            for status, ramp in STATUS_RAMPS.items():
                for half in (False, True):
                    kind = "half" if half else "full"
                    pack.png(f"{base}/{status}{hp}{kind}{b}.png", heart_fill(ramp, half, hc, blink))
    # vehicle (horse) hearts
    pack.png(f"{base}/vehicle_container.png", heart_container(interior="#2a1d17"))
    pack.png(f"{base}/vehicle_full.png", heart_fill(HEART_VEHICLE))
    pack.png(f"{base}/vehicle_half.png", heart_fill(HEART_VEHICLE, half=True))


# =============================================================================
# Food (drumstick), armour (chestplate), air bubbles
# =============================================================================
def _outline_cells(fill: set[tuple[int, int]], size: int = 9) -> set[tuple[int, int]]:
    out = set()
    for x, y in fill:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                c = (x + dx, y + dy)
                if c not in fill and 0 <= c[0] < size and 0 <= c[1] < size:
                    out.add(c)
    return out


# drumstick: round meat top-left, thin bone neck, knob bottom-right (fill lives inside x,y = 1..7)
FOOD_MEAT = ({(x, 1) for x in range(2, 6)} | {(x, 2) for x in range(1, 7)} | {(x, 3) for x in range(1, 7)}
             | {(x, 4) for x in range(1, 6)} | {(x, 5) for x in range(2, 5)})
FOOD_BONE = {(5, 5), (6, 6), (7, 6), (6, 7), (7, 7)}
FOOD_FILL = FOOD_MEAT | FOOD_BONE
FOOD_OUTLINE = _outline_cells(FOOD_FILL)

MEAT = Ramp("#7d3b1e", "#b8622f", "#e08a4c", "#ffc491")
MEAT_HUNGER = Ramp("#4c5a1c", "#7b8d33", "#a3b552", "#d2e08d")


def food_container() -> Sprite:
    s = Sprite(9, 9)
    for x, y in FOOD_FILL:
        s.set(x, y, SLOT_DARK)
    for x, y in FOOD_OUTLINE:
        s.set(x, y, INK)
    return s


def food_fill(ramp: Ramp, half: bool = False) -> Sprite:
    s = Sprite(9, 9)
    for x, y in sorted(FOOD_FILL):
        if half and x > 4:
            continue
        if (x, y) in FOOD_BONE:
            c = "#f6f1e4" if (x, y) in {(7, 6), (6, 7)} else "#d8d0bc"
        elif (x, y) == (2, 2):
            c = ramp.s
        elif (x, y) in {(1, 2), (2, 1), (3, 1), (1, 3), (3, 2)}:
            c = ramp.l
        elif x + y >= 8:
            c = ramp.d
        else:
            c = ramp.m
        s.set(x, y, c)
    return s


# chestplate: wide shoulders, narrower torso
ARMOR_FILL = ({(x, 1) for x in (1, 2, 3, 5, 6, 7)} | {(x, 2) for x in range(1, 8)}
              | {(x, y) for y in range(3, 8) for x in range(2, 7)})
ARMOR_OUTLINE = _outline_cells(ARMOR_FILL)


def armor_icon(state: str) -> Sprite:
    s = Sprite(9, 9)
    for x, y in ARMOR_FILL:
        lit = state == "full" or (state == "half" and x <= 4)
        if lit:
            if (x, y) in {(1, 1), (2, 1), (2, 2)}:
                c = "#ffffff"
            elif x <= 3:
                c = "#e6e8eb"
            elif x <= 5:
                c = "#c0c4ca"
            else:
                c = "#8f949d"
            if y >= 6:
                c = mix(c, "#2b2d33", 0.18)
        else:
            c = "#3a3b43"
        s.set(x, y, c)
    for x, y in ARMOR_OUTLINE:
        s.set(x, y, INK)
    return s


AIR_BUBBLE = [
    "..OOOOO..",
    ".OhhmmmO.",
    "OhwhmmmbO",
    "OhhmmmmbO",
    "OmmmmmmbO",
    "OmmmmmbbO",
    "OmmmmbbbO",
    ".ObbbbbO.",
    "..OOOOO..",
]
AIR_LEGEND = {"O": "#1f5a8f", "h": "#e6f7ff", "w": "#ffffff", "m": "#8ccbf7", "b": "#4b9ce0"}


def air(kind: str) -> Sprite:
    if kind == "air":
        return Sprite.from_ascii(AIR_BUBBLE, AIR_LEGEND)
    s = Sprite(9, 9)
    if kind == "bursting":
        for x, y in ((0, 0), (1, 1), (7, 1), (8, 0), (0, 8), (1, 7), (7, 7), (8, 8), (4, 0), (4, 8), (0, 4), (8, 4)):
            s.set(x, y, "#4fb4f0")
        for x, y in ((2, 2), (6, 2), (2, 6), (6, 6)):
            s.set(x, y, "#a7e2ff")
    else:                                          # empty
        s.disc(4.5, 4.5, 1.8, "#101114")
        s.disc(4.5, 4.5, 1.0, "#2c2d33")
    return s


# =============================================================================
# Bars (182x5): experience, horse jump
# =============================================================================
def bar_background() -> Sprite:
    s = Sprite(182, 5).fill(with_alpha(INK, 235))
    s.rect(1, 1, 180, 3, with_alpha("#1c1d22", 235))
    for x in range(10, 181, 10):                   # faint segment marks like vanilla
        s.set(x, 2, with_alpha("#0c0d10", 255))
    return s


def bar_progress(top: str, mid: str, low: str, mark: str) -> Sprite:
    s = Sprite(182, 5)
    s.rect(0, 0, 182, 1, with_alpha(INK, 235))
    s.rect(0, 4, 182, 1, with_alpha(INK, 235))
    s.rect(0, 0, 1, 5, with_alpha(INK, 235))
    s.rect(181, 0, 1, 5, with_alpha(INK, 235))
    s.rect(1, 1, 180, 1, top)
    s.rect(1, 2, 180, 1, mid)
    s.rect(1, 3, 180, 1, low)
    for x in range(10, 181, 10):
        s.set(x, 2, mark)
        s.set(x, 3, mark)
    return s


def effect_bg(ambient: bool) -> Sprite:
    s = Sprite(24, 24)
    edge = theme.ACCENT if ambient else theme.PANEL_EDGE
    s.rect(1, 0, 22, 24, with_alpha(INK, 235))
    s.rect(0, 1, 24, 22, with_alpha(INK, 235))
    s.rect(1, 1, 22, 22, edge)
    s.rect(2, 2, 20, 20, with_alpha("#15161a", 235))
    s.rect(2, 2, 20, 1, with_alpha(mix(edge, "#ffffff", 0.2), 60))
    return s


# =============================================================================
def generate(pack) -> None:
    pack.png(f"{SP}/hotbar.png", hotbar())
    pack.png(f"{SP}/hotbar_selection.png", selection())
    pack.png(f"{SP}/hotbar_offhand_left.png", offhand(True))
    pack.png(f"{SP}/hotbar_offhand_right.png", offhand(False))
    pack.png(f"{SP}/crosshair.png", crosshair())
    pack.png(f"{SP}/crosshair_attack_indicator_full.png", indicator_full())
    pack.png(f"{SP}/crosshair_attack_indicator_background.png", indicator_bg())
    pack.png(f"{SP}/crosshair_attack_indicator_progress.png", indicator_progress())
    pack.png(f"{SP}/hotbar_attack_indicator_background.png", hotbar_indicator(False))
    pack.png(f"{SP}/hotbar_attack_indicator_progress.png", hotbar_indicator(True))
    hearts(pack)
    pack.png(f"{SP}/food_empty.png", food_container())
    pack.png(f"{SP}/food_empty_hunger.png", food_container())
    pack.png(f"{SP}/food_full.png", food_fill(MEAT))
    pack.png(f"{SP}/food_half.png", food_fill(MEAT, half=True))
    pack.png(f"{SP}/food_full_hunger.png", food_fill(MEAT_HUNGER))
    pack.png(f"{SP}/food_half_hunger.png", food_fill(MEAT_HUNGER, half=True))
    pack.png(f"{SP}/armor_empty.png", armor_icon("empty"))
    pack.png(f"{SP}/armor_half.png", armor_icon("half"))
    pack.png(f"{SP}/armor_full.png", armor_icon("full"))
    pack.png(f"{SP}/air.png", air("air"))
    pack.png(f"{SP}/air_bursting.png", air("bursting"))
    pack.png(f"{SP}/air_empty.png", air("empty"))
    pack.png(f"{SP}/experience_bar_background.png", bar_background())
    pack.png(f"{SP}/experience_bar_progress.png", bar_progress("#c4ff8a", "#74d940", "#3f9a25", "#2f7a1c"))
    pack.png(f"{SP}/jump_bar_background.png", bar_background())
    pack.png(f"{SP}/jump_bar_progress.png", bar_progress(theme.ACCENT_LIGHT, theme.ACCENT, theme.ACCENT_DARK, "#126a86"))
    pack.png(f"{SP}/jump_bar_cooldown.png", bar_progress("#c3ccd8", "#8794a6", "#5a6678", "#47515f"))
    pack.png(f"{SP}/effect_background.png", effect_bg(False))
    pack.png(f"{SP}/effect_background_ambient.png", effect_bg(True))
