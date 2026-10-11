"""Worn armour -- what players see on each other (and on armour stands / mobs).

Both humanoid layers are identical on 1.21.11, 26.1.2, 26.2 and 26.3, so they live in the shared
base layer of the pack.  The art matches the SushantLite armour icons: a bevelled plate in the
material's colours, a darker trim at collars, cuffs and knees, and the cyan signature gem on the
helmet, chestplate and belt buckle.

Texture layout (64x32, UV unwrap of the standard humanoid cuboids -- see ``uv.py``)::

    head  texOffs( 0, 0)  8 x  8 x 8        right arm / left arm  texOffs(40, 16)  4 x 12 x 4
    body  texOffs(16,16)  8 x 12 x 4        right leg / left leg  texOffs( 0, 16)  4 x 12 x 4

(the left arm and leg reuse the right-hand patch, mirrored -- so nothing here is left/right
asymmetric).  Which cells of that layout each armour piece paints is decided by the *rules*
below; the resulting masks equal the opaque-pixel masks of vanilla's iron, copper and gold textures
(analysis only, nothing copied):

    layer 1 ``humanoid``           helmet : head top + rows 8-10 all round, nasal/cheek tabs, neck guard
                                   chest  : body rows 20-28 (+ a front taper), arm tops + rows 20-24
                                   boots  : leg soles + rows 26-31
    layer 2 ``humanoid_leggings``  belt   : body rows 27-31          legs : leg tops + rows 20-28

Leather (dyeable) and turtle-shell armour and baby-sized armour (26.1+) stay vanilla (the elytra is in ``wings.py``).
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import theme
from ..sprite import Sprite, mix
from ..theme import ARMOR_ORDER, MATERIALS, TRIM, Ramp
from ..uv import Rect, box_faces, rect_cells, sub_rows

EQUIP = "assets/minecraft/textures/entity/equipment"

HEAD = box_faces(0, 0, 8, 8, 8)
BODY = box_faces(16, 16, 8, 12, 4)
ARM = box_faces(40, 16, 4, 12, 4)
LEG = box_faces(0, 16, 4, 12, 4)
SIDES = ("west", "front", "east", "back")


# --------------------------------------------------------------------------- regions
@dataclass
class Region:
    piece: str                 # helmet | chest | boots | belt | legs
    face: str                  # top | bottom | west | front | east | back
    rect: Rect                 # the face's full rectangle (origin of the local coordinates)
    cells: set                 # texture pixels this piece paints on that face


def _region(piece: str, face: str, rect: Rect, cells: set) -> Region:
    return Region(piece, face, rect, cells)


def layer1_regions() -> list[Region]:
    out: list[Region] = []

    # ---- helmet -------------------------------------------------------------------------
    out.append(_region("helmet", "top", HEAD["top"], rect_cells(HEAD["top"])))
    for face in SIDES:
        r = HEAD[face]
        cells = rect_cells(sub_rows(r, 8, 10))                       # the band round the head
        if face == "front":
            cells |= {(x, 11) for x in (8, 11, 12, 15)} | {(11, 12), (12, 12)}   # cheeks + nasal guard
        elif face == "west":
            cells |= {(x, 11) for x in range(0, 8)} | {(x, 12) for x in range(0, 4)}
        elif face == "east":
            cells |= {(x, 11) for x in range(16, 24)} | {(x, 12) for x in range(20, 24)}
        else:                                                         # back: neck guard
            cells |= rect_cells(sub_rows(r, 11, 13)) | {(x, 14) for x in range(26, 30)}
        out.append(_region("helmet", face, r, cells))

    # ---- chestplate ---------------------------------------------------------------------
    for face in SIDES:
        r = BODY[face]
        cells = rect_cells(sub_rows(r, 20, 28))
        if face == "front":
            cells -= {(x, 20) for x in range(22, 26)} | {(23, 21), (24, 21)}   # V-shaped neck opening
            cells |= {(x, 29) for x in range(21, 27)} | {(x, 30) for x in range(22, 26)}   # taper
        elif face == "back":
            cells -= {(x, 20) for x in range(34, 38)}
            cells |= {(x, 29) for x in range(33, 39)}
        out.append(_region("chest", face, r, cells))
    out.append(_region("chest", "top", ARM["top"], rect_cells(ARM["top"])))              # shoulder
    for face in SIDES:
        out.append(_region("chest", face, ARM[face], rect_cells(sub_rows(ARM[face], 20, 24))))

    # ---- boots --------------------------------------------------------------------------
    out.append(_region("boots", "bottom", LEG["bottom"], rect_cells(LEG["bottom"])))      # sole
    for face in SIDES:
        out.append(_region("boots", face, LEG[face], rect_cells(sub_rows(LEG[face], 26, 31))))
    return out


def layer2_regions() -> list[Region]:
    out: list[Region] = []
    for face in SIDES:                                                # belt / hips
        out.append(_region("belt", face, BODY[face], rect_cells(sub_rows(BODY[face], 27, 31))))
    out.append(_region("legs", "top", LEG["top"], rect_cells(LEG["top"])))
    for face in SIDES:
        out.append(_region("legs", face, LEG[face], rect_cells(sub_rows(LEG[face], 20, 28))))
    return out


# --------------------------------------------------------------------------- materials
@dataclass(frozen=True)
class Style:
    ramp: Ramp
    trim: Ramp
    kind: str                  # metal | mail | shiny | dark


STYLES = {
    "copper": Style(MATERIALS["copper"], TRIM["copper"], "metal"),
    "chainmail": Style(MATERIALS["chainmail"], TRIM["chainmail"], "mail"),
    "iron": Style(MATERIALS["iron"], TRIM["iron"], "metal"),
    "golden": Style(MATERIALS["golden"], TRIM["golden"], "shiny"),
    "diamond": Style(MATERIALS["diamond"], TRIM["diamond"], "shiny"),
    "netherite": Style(MATERIALS["netherite"], TRIM["netherite"], "dark"),
}
FILE_NAMES = {"copper": "copper", "chainmail": "chainmail", "iron": "iron",
              "golden": "gold", "diamond": "diamond", "netherite": "netherite"}   # vanilla's file names


def _hash(x: int, y: int) -> int:
    return ((x * 73856093) ^ (y * 19349663) ^ (x * y * 83492791)) % 100


def surface(st: Style, x: int, y: int, lit: bool, dark: bool, trim: bool = False) -> str:
    """One pixel of plate: bevel from the face edges plus a little deterministic speckle."""
    r = st.trim if trim else st.ramp
    if st.kind == "mail" and not trim:
        woven = (x + y) % 2 == 0
        if lit and woven:
            return r.s
        if dark and not woven:
            return r.d
        return r.l if woven else r.d if (x // 2 + y) % 3 == 0 else r.m
    if lit and not dark:
        return r.l
    if dark and not lit:
        return r.d
    h = _hash(x, y)
    if h < 6:
        return r.l
    if h < 13:
        return r.d
    if st.kind == "shiny" and h > 96:
        return r.s
    if st.kind == "dark" and 40 <= h < 44:
        return r.l
    return r.m


GEM = (("#c9f7ff", theme.ACCENT), (theme.ACCENT, theme.ACCENT_DARK))      # 2x2 lit facet / shadow facet


def gem_pixel(lx: int, ly: int) -> str:
    return GEM[ly][lx]


# --------------------------------------------------------------------------- per-piece colouring
def colour(st: Style, reg: Region, x: int, y: int, lit: bool, dark: bool) -> str:
    rx, ry, _w, _h = reg.rect
    lx, ly = x - rx, y - ry
    face, piece = reg.face, reg.piece
    plate = lambda trim=False: surface(st, x, y, lit, dark, trim)         # noqa: E731

    # ------------------------------------------------------------------ helmet
    if piece == "helmet":
        if face == "top":
            if lx in (3, 4):                                              # centre crest
                return st.trim.l if lx == 3 else st.trim.m
            if (lx, ly) in ((1, 1), (6, 1), (1, 6), (6, 6)):
                return st.ramp.s
            return plate()
        if face == "front":
            if y <= 9 and lx in (3, 4):                                   # brow gem
                return gem_pixel(lx - 3, y - 8)
            if y >= 11:
                return plate(trim=True)                                   # nasal guard + cheeks
            return plate()
        if face in ("west", "east") and y >= 11:
            return plate(trim=True)
        if face == "back" and lx in (3, 4) and y <= 13:                   # centre seam
            return st.ramp.d if lx == 3 else st.ramp.l
        return plate()

    # ------------------------------------------------------------------ chestplate
    if piece == "chest":
        if reg.rect in (ARM["top"],) or any(reg.rect == ARM[f] for f in SIDES):
            if face == "top":                                             # shoulder cap
                return st.ramp.s if (lx, ly) in ((1, 1), (2, 2)) else plate(trim=True)
            return plate(trim=(y <= 21))                                  # shoulder strap rows
        # body
        if y == 20 and face in ("front", "back"):                         # collar
            return plate(trim=True)
        if face == "front":
            if lx in (3, 4) and 22 <= y <= 23:                            # chest gem
                return gem_pixel(lx - 3, y - 22)
            if y == 26:
                return st.trim.d                                          # waist line
            if y == 27:
                return st.trim.m
            if lx in (3, 4) and 24 <= y <= 25:                            # sternum seam
                return st.ramp.d if lx == 3 else st.ramp.l
        if face == "back" and lx in (3, 4) and y >= 21:                   # spine seam
            return st.ramp.d if lx == 3 else st.ramp.l
        return plate()

    # ------------------------------------------------------------------ boots
    if piece == "boots":
        if face == "bottom":
            return st.trim.d if (lx + ly) % 2 == 0 else st.trim.m         # tread
        if y <= 27:                                                       # cuff
            if face == "front" and y == 27 and lx in (1, 2):              # cuff rivets
                return theme.ACCENT if lx == 1 else theme.ACCENT_DARK
            return plate(trim=True)
        return plate()

    # ------------------------------------------------------------------ leggings (layer 2)
    if piece == "belt":
        if y <= 28:                                                       # strap
            if face == "front" and lx in (3, 4):                          # buckle
                return gem_pixel(lx - 3, y - 27)
            return plate(trim=True)
        if face == "front" and lx in (3, 4):
            return st.ramp.d if lx == 3 else st.ramp.l
        return plate()
    if piece == "legs":
        if face == "top":
            return plate()
        if 24 <= y <= 25:                                                 # knee guard (the boots start at row 26)
            return plate(trim=True)
        return plate()
    return plate()


# --------------------------------------------------------------------------- assembly
def build_layer(regions: list[Region], st: Style) -> Sprite:
    s = Sprite(64, 32)
    for reg in regions:
        cells = reg.cells
        for (x, y) in cells:
            lit = (x, y - 1) not in cells or (x - 1, y) not in cells
            dark = (x, y + 1) not in cells or (x + 1, y) not in cells
            s.set(x, y, colour(st, reg, x, y, lit, dark))
    return s


def coverage(regions: list[Region]) -> set:
    return {c for reg in regions for c in reg.cells}


def textures() -> dict[str, tuple[Sprite, Sprite]]:
    """material -> (layer 1, layer 2)"""
    l1, l2 = layer1_regions(), layer2_regions()
    return {m: (build_layer(l1, STYLES[m]), build_layer(l2, STYLES[m])) for m in ARMOR_ORDER}


def generate(pack) -> None:
    for material, (outer, inner) in textures().items():
        name = FILE_NAMES[material]
        pack.png(f"{EQUIP}/humanoid/{name}.png", outer)
        pack.png(f"{EQUIP}/humanoid_leggings/{name}.png", inner)
