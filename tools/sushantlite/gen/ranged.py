"""Crossbow and trident icons.  (The bow and arrow live in ``items.py``.)

Both are drawn from geometry rather than ASCII so the crossbow's pull animation stays consistent:
the stock is fixed, the limbs flex back and the string follows.

Crossbow, pointing up-right.  The stock lies on the diagonal x + y = 15, the limb is a quadratic
Bezier between two tips mirrored across that axis, and ``pull`` moves the string's nock point back
along the axis (d = 0 at rest ... 3.5 fully drawn / loaded).

Trident: the shaft on the same diagonal, a cross-piece perpendicular to it, three cyan prongs.
(Its worn / thrown 3D texture is in ``entities.py``.)
"""
from __future__ import annotations

from .. import theme
from ..sprite import Sprite, mix
from ..theme import Ramp
from .items import shade_part

ITEM = "assets/minecraft/textures/item"

WOOD = Ramp("#4a2e12", "#6f4721", "#9a6a35", "#c79656")
STEEL = Ramp("#2f3946", "#56677a", "#8497ab", "#c9d6e4")
NAVY = theme.NAVY
SHAFT = "#d9b878"


def _bezier(p0, c, p1, n: int = 64):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * c[0] + t * t * p1[0],
                    (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * c[1] + t * t * p1[1]))
    return pts


NOCK_BACK = {-1: 0.0, 0: 1.5, 1: 2.5, 2: 3.5}      # how far the string is drawn for each icon


def crossbow(pull: int = -1, load: str | None = None) -> Sprite:
    """pull: -1 standby, 0..2 being drawn; ``load``: None | 'arrow' | 'rocket' (string fully drawn)."""
    d = 3.5 if load else NOCK_BACK[pull]
    s = Sprite(16, 16)

    # --- stock: 2px thick diagonal from the butt (2, 13) to the front (11, 4)
    stock = set()
    for i in range(10):
        stock |= {(2 + i, 13 - i), (3 + i, 13 - i)}
    stock -= {(12, 4)}
    for x, y in stock:
        s.set(x, y, shade_part(x, y, stock, WOOD))
    s.set(2, 13, theme.ACCENT)                                     # signature gem on the butt
    s.set(3, 13, theme.ACCENT_DARK)
    for x, y in ((6, 10), (7, 10)):                                # trigger housing
        s.set(x, y, WOOD.d)

    # --- limb (steel): tips mirrored across x + y = 15, control point flexes back with the draw
    t1, t2 = (7.0, 1.0), (14.0, 8.0)
    control = (13.5 - 0.5 * d, 1.5 + 0.5 * d)
    limb = set()
    n = 64
    for i, (x, y) in enumerate(_bezier(t1, control, t2, n)):
        cell = (int(x), int(y))
        limb.add(cell)
        if 0.18 < i / n < 0.82:                                    # 2px in the middle, 1px at the tips
            limb.add((cell[0] + 1, cell[1]) if (x + y) < 15.0 else (cell[0], cell[1] + 1))
    limb -= stock
    solid = limb | stock
    for x, y in limb:
        s.set(x, y, shade_part(x, y, solid, STEEL))
    s.set(7, 1, theme.ACCENT_LIGHT)                                # limb tips glow
    s.set(14, 8, theme.ACCENT_DARK)

    # --- string: from both tips back to the nock point on the stock axis
    mid = ((t1[0] + t2[0]) / 2, (t1[1] + t2[1]) / 2)
    nock = (round(mid[0] - d), round(mid[1] + d))
    string = "#dce8f0"
    s.line(round(t1[0]), round(t1[1]) + 1, nock[0], nock[1], string)
    s.line(round(t2[0]) - 1, round(t2[1]), nock[0], nock[1], string)

    # --- loaded projectile, resting on the stock (one step up-left of the axis)
    if load == "arrow":
        for i, (x, y) in enumerate(((6, 8), (7, 7), (8, 6), (9, 5), (10, 4), (11, 3), (12, 2))):
            s.set(x, y, SHAFT if i % 2 == 0 else "#bf9d5c")
        s.set(5, 9, theme.ACCENT)                                  # fletching
        s.set(6, 8, "#f4fbff")
        s.points([(13, 1), (13, 2), (12, 1)], "#c8d3dc")
        s.set(13, 1, "#ffffff")
    elif load == "rocket":
        body = {(7, 7), (8, 7), (8, 6), (9, 6), (9, 5), (10, 5), (10, 4), (11, 4), (11, 3)}
        for x, y in body:
            s.set(x, y, theme.RED.m if (x + y) % 2 else theme.RED.l)
        for x, y in ((8, 6), (9, 5)):
            s.set(x, y, "#f4fbff")                                 # paper band
        s.points([(12, 3), (12, 2), (11, 2)], "#f4fbff")           # nose cone
        s.set(13, 1, theme.ORANGE.s)                               # fuse spark
        s.set(12, 1, theme.ORANGE.m)
        s.points([(6, 8), (6, 7), (7, 8)], theme.ACCENT)           # fins
    s.outline(theme.INK)
    return s


def trident() -> Sprite:
    s = Sprite(16, 16)
    # shaft: butt gem -> up-right, a ring of cyan, and a lighter highlight pixel every 3rd step
    shaft = [(2 + i, 13 - i) for i in range(8)]                    # (2,13) .. (9,6)
    for i, (x, y) in enumerate(shaft):
        s.set(x, y, NAVY.l if i % 3 == 1 else NAVY.m)
        s.set(x + 1, y, NAVY.d) if i not in (0, 7) and (x + 1, y) not in shaft else None
    s.set(2, 13, theme.ACCENT)
    s.set(5, 10, theme.ACCENT_DARK)
    s.set(6, 9, theme.ACCENT)
    # cross-piece perpendicular to the shaft
    cross = [(7, 4), (8, 5), (9, 6), (10, 7), (11, 8)]
    for i, (x, y) in enumerate(cross):
        s.set(x, y, STEEL.l if i < 2 else STEEL.m if i == 2 else STEEL.d)
    s.set(9, 6, theme.ACCENT)                                      # centre stud
    # three prongs, bright at the tip
    ramp = [theme.ACCENT_DARK, theme.ACCENT, theme.ACCENT_LIGHT, "#e4fffb"]
    for (x0, y0), length in (((10, 5), 5), ((8, 3), 3), ((12, 7), 3)):
        for k in range(length):
            shade = ramp[min(3, int(k * 4 / length))]
            s.set(x0 + k, y0 - k, shade)
    s.outline(theme.INK)
    return s


def generate(pack) -> None:
    pack.png(f"{ITEM}/crossbow_standby.png", crossbow(-1))
    for i in range(3):
        pack.png(f"{ITEM}/crossbow_pulling_{i}.png", crossbow(i))
    pack.png(f"{ITEM}/crossbow_arrow.png", crossbow(2, "arrow"))
    pack.png(f"{ITEM}/crossbow_firework.png", crossbow(2, "rocket"))
    pack.png(f"{ITEM}/trident.png", trident())
