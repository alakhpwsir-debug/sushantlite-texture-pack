"""Item textures: weapons, tools and the PvP consumables.

Tools are authored as ASCII *masks* (which pixel belongs to which part of the
tool); colour, bevel shading and the dark outline are then added automatically:

* light comes from the top-left: lit edges use the ramp's light tone, shadow
  edges (bottom/right) the dark tone, everything else the mid tone,
* every sprite gets a one-pixel near-black outline.

Look: bold, vanilla-proportioned silhouettes.  The sword blade is three pixels wide, so the shading
reads as a lit edge, a body and a shadow edge (that gradient is what shows in first person).
Diamond tools are blue and netherite tools violet (``theme.TOOL_HEADS``); there is no decoration
on the handle any more.

Mask legend
    B  head / blade (material ramp)        T  guard / socket (trim ramp)
    H  handle (wood)                       P  pommel (wood)
    S  spike (trim ramp)
"""
from __future__ import annotations

from .. import theme
from ..sprite import Sprite, mix, rgba, with_alpha
from ..theme import ARMOR_ORDER, HANDLE, MATERIAL_ORDER, MATERIALS, TRIM, Ramp

ITEM = "assets/minecraft/textures/item"

# --------------------------------------------------------------------------- masks (16x16)
SWORD = [
    "................",
    "..............B.",
    ".............BB.",
    "............BB..",
    "...........BBB..",
    "..........BBB...",
    ".........BBB....",
    "........BBB.....",
    "...TT..BBB......",
    "....TTBBB.......",
    ".....TT.........",
    "....H.TT........",
    "...H...TT.......",
    ".PP.............",
    ".PP.............",
    "................",
]

PICKAXE = [
    "................",
    "................",
    "........BBBBB...",
    "......BBBBBBBB..",
    "....BBBB..BBBB..",
    "...BB.....TBBB..",
    ".........H..BB..",
    "........H...BB..",
    ".......H...BB...",
    "......H....BB...",
    ".....H.....B....",
    "....H......B....",
    "...H......B.....",
    "..H.............",
    "................",
    "................",
]

AXE = [
    "................",
    ".......BBB......",
    "......BBBBB.....",
    ".....BBBBBBB....",
    "....BBBBBBBHB...",
    "....BBBBBBHB....",
    "....BB..BH......",
    "....B...H.......",
    ".......H........",
    "......H.........",
    ".....H..........",
    "....H...........",
    "...H............",
    "..H.............",
    "................",
    "................",
]

SHOVEL = [
    "................",
    "................",
    "...........BBBB.",
    "..........BBBB..",
    ".........BBBB...",
    "........BBBBB...",
    ".......BBBBB....",
    ".......BBBB.....",
    ".......H........",
    "......H.........",
    ".....H..........",
    "....H...........",
    "...H............",
    "..H.............",
    "................",
    "................",
]

HOE = [
    "................",
    "......BB........",
    ".....BBBB.......",
    "....BB..BB......",
    "...BB....BB.....",
    "..BB......H.....",
    ".........H......",
    "........H.......",
    ".......H........",
    "......H.........",
    ".....H..........",
    "....H...........",
    "...H............",
    "..H.............",
    "................",
    "................",
]

SPEAR = [
    "................",
    "..............B.",
    ".............BB.",
    "...........BBBB.",
    "..........BBBB..",
    ".........BBBB...",
    ".........BB.....",
    "........TT......",
    ".......H........",
    "......H.........",
    ".....H..........",
    "....H...........",
    "...H............",
    "..H.............",
    "................",
    "................",
]

MACE = [
    "................",
    "...........S....",
    "..........BBB...",
    ".........BBBBB..",
    "........SBBBBBS.",
    ".........BBBBB..",
    ".........HBBB...",
    "........H..S....",
    ".......H........",
    "......H.........",
    ".....H..........",
    "....H...........",
    "...H............",
    "..H.............",
    "................",
    "................",
]


# armour (legend: B plate, T trim); all symmetric about the vertical axis
HELMET = [
    "................",
    "................",
    "................",
    ".....BBBBBB.....",
    "....BBBBBBBB....",
    "...BBBBBBBBBB...",
    "...BBBBBBBBBB...",
    "...BBBBBBBBBB...",
    "...TTTTTTTTTT...",
    "...BBB....BBB...",
    "...BBB....BBB...",
    "...BB......BB...",
    "................",
    "................",
    "................",
    "................",
]

CHESTPLATE = [
    "................",
    "................",
    "..BBB......BBB..",
    ".BBBBB....BBBBB.",
    ".BBBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBB..",
    "..BBBBBBBBBBBB..",
    "...BBBBTTBBBB...",
    "...BBBBTTBBBB...",
    "...BBBBTTBBBB...",
    "...BBBBTTBBBB...",
    "...BBBBBBBBBB...",
    "....BBBBBBBB....",
    "....TTTTTTTT....",
    "................",
    "................",
]

LEGGINGS = [
    "................",
    "................",
    "...TTTTTTTTTT...",
    "...BBBBBBBBBB...",
    "...BBBBBBBBBB...",
    "...BBBBBBBBBB...",
    "...BBBBBBBBBB...",
    "...BBBB..BBBB...",
    "...BBBB..BBBB...",
    "...BBBB..BBBB...",
    "...BBBB..BBBB...",
    "...BBBB..BBBB...",
    "...BBBB..BBBB...",
    "...TTTT..TTTT...",
    "................",
    "................",
]

BOOTS = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "....BBB....BBB..",
    "..BBBBB..BBBBB..",
    "..BBBBB..BBBBB..",
    "..TTTTT..TTTTT..",
    "................",
    "................",
    "................",
]

# --------------------------------------------------------------------------- rendering helpers
def _cells(rows):
    return {(x, y): ch for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != "."}


def shade_part(x: int, y: int, solid: set, ramp: Ramp) -> str:
    lit = (x, y - 1) not in solid or (x - 1, y) not in solid
    dark = (x, y + 1) not in solid or (x + 1, y) not in solid
    if lit and not dark:
        return ramp.l
    if dark and not lit:
        return ramp.d
    return ramp.m


def render_mask(rows, ramps: dict, outline=theme.INK, shine=(), handle_pattern: bool = True) -> Sprite:
    cells = _cells(rows)
    solid = set(cells)
    h, w = len(rows), len(rows[0])
    s = Sprite(w, h)
    for (x, y), ch in cells.items():
        part = ramps[ch]
        if isinstance(part, str):
            colour = part
        elif ch in "HP" and handle_pattern:
            colour = part.l if (x + y) % 5 == 0 else part.d if (x % 3 == 0) else part.m
        else:
            colour = shade_part(x, y, solid, part)
        s.set(x, y, colour)
    for x, y in shine:
        ch = cells.get((x, y))
        if ch and isinstance(ramps[ch], Ramp):
            s.set(x, y, ramps[ch].s)
    s.outline(outline)
    return s


def tool_ramps(material: str) -> dict:
    head = theme.TOOL_HEADS.get(material, MATERIALS[material])
    trim = theme.TOOL_TRIM.get(material, TRIM[material])
    handle = HANDLE if material != "wooden" else Ramp("#4a2e12", "#6b4520", "#8d5f2d", "#aa7a3f")
    return {"B": head, "T": trim, "S": trim, "H": handle, "P": handle}


def _tip(rows) -> tuple[int, int]:
    """The 'B' cell furthest to the upper right (largest x - y) -> gets the shine pixel."""
    best = max(((x - y, x, y) for (x, y), ch in _cells(rows).items() if ch == "B"))
    return best[1], best[2]


SWORD_GLINT = [(11, 4), (9, 6), (7, 8)]       # every other cell of the lit edge shines


def tool(rows, material: str, extra_shine=()) -> Sprite:
    shine = [_tip(rows), *extra_shine]
    return render_mask(rows, tool_ramps(material), shine=shine)


def armor_piece(rows, material: str) -> Sprite:
    """Armour icons share the tool pipeline; chainmail gets a dithered mesh look."""
    plate, trim = MATERIALS[material], TRIM[material]
    ramps = {"B": plate, "T": trim}
    s = render_mask(rows, ramps, shine=[])
    if material == "chainmail":
        for (x, y), ch in _cells(rows).items():
            if ch == "B":
                base = s.get(x, y)
                if (x + y) % 2 == 0:
                    s.set(x, y, mix(base, plate.s, 0.30))
                else:
                    s.set(x, y, mix(base, plate.d, 0.35))
    else:
        # one glint pixel on the top-left shoulder / dome so metal reads as metal
        cells = [(x, y) for (x, y), ch in _cells(rows).items() if ch == "B"]
        gx, gy = min(cells, key=lambda c: (c[1] + c[0] * 0.5, c[0]))
        s.set(gx, gy, plate.s)
    return s


# --------------------------------------------------------------------------- spear, in hand (32x32)
def spear_in_hand(material: str) -> Sprite:
    """32x32 in-hand spear: head at the top-left, thin shaft down to the bottom-right."""
    ramps = tool_ramps(material)
    head = ramps["B"]
    trim = ramps["T"]
    # head: mirror the icon's head (x -> 15 - x), then scale x2
    base = _cells(SPEAR)
    cells: dict[tuple[int, int], str] = {}
    for (x, y), ch in base.items():
        if ch in "BT":
            mx = 15 - x
            for dx in (0, 1):
                for dy in (0, 1):
                    cells[(mx * 2 + dx, y * 2 + dy)] = ch
    # shaft: 1px diagonal from just below the socket to the butt
    start = (min(x for (x, y), c in cells.items() if c == "T" or c == "B") + 4, 0)
    sx0 = max(x for (x, y), c in cells.items() if c == "T")
    sy0 = max(y for (x, y), c in cells.items() if c == "T")
    n = 0
    x, y = sx0 + 1, sy0 + 1
    while x <= 28 and y <= 28:
        cells[(x, y)] = "H"
        x, y = x + 1, y + 1
        n += 1
    # butt cap
    cells[(x, y)] = "T"
    cells[(x - 1, y - 1)] = "T"
    # band of colour on the shaft
    solid = set(cells)
    s = Sprite(32, 32)
    for (x, y), ch in cells.items():
        part = ramps[ch]
        if isinstance(part, str):
            colour = part
        elif ch == "H":
            colour = part.l if (x // 2) % 4 == 0 else part.d if (x // 2) % 4 == 2 else part.m
        else:
            colour = shade_part(x, y, solid, part)
        s.set(x, y, colour)
    # leather wrap halfway down the shaft
    mid = (sx0 + 1 + x) // 2
    for k in (0, 2):
        s.set(mid + k, mid + k, trim.m)
        s.set(mid + k + 1, mid + k + 1, trim.d)
    # shine on the spear tip
    tx = min(px for (px, py), c in cells.items() if c == "B")
    ty = min(py for (px, py), c in cells.items() if c == "B" and px == tx)
    s.set(tx, ty, head.s)
    s.outline(theme.INK)
    return s


# --------------------------------------------------------------------------- generic helpers
def _disc_cells(cx: float, cy: float, r: float, size: int = 16) -> set:
    return {(x, y) for y in range(size) for x in range(size) if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r}


def shaded(cells: set, ramp: Ramp, s: Sprite | None = None, size: int = 16) -> Sprite:
    s = s or Sprite(size, size)
    for x, y in cells:
        s.set(x, y, shade_part(x, y, cells, ramp))
    return s


# --------------------------------------------------------------------------- consumables
def totem() -> Sprite:
    """Gold idol with a green face and an emerald in its chest."""
    rows = [
        "................",
        ".....GGGGGG.....",
        "....GGGGGGGG....",
        "....GGGGGGGG....",
        "....GGGGGGGG....",
        "....GGGGGGGG....",
        ".....GGGGGG.....",
        "..GGGGGGGGGGGG..",
        "..GGGGGGGGGGGG..",
        "...GG.GGGG.GG...",
        "......GGGG......",
        "......GGGG......",
        ".....GGGGGG.....",
        ".....GGGGGG.....",
        "....GGGGGGGG....",
        "................",
    ]
    gold, skin = theme.GOLD, theme.GREEN
    s = render_mask(rows, {"G": gold}, outline=theme.INK)
    for y in range(2, 6):                              # face: a green panel inside the gold frame
        for x in range(5, 11):
            s.set(x, y, skin.l if (x == 5 or y == 2) else skin.d if (x == 10 or y == 5) else skin.m)
    s.set(5, 2, skin.s)
    for x, y in ((6, 3), (9, 3)):                      # eyes
        s.set(x, y, "#10200e")
    for x, y in ((7, 5), (8, 5)):                      # mouth
        s.set(x, y, "#5b3210")
    s.set(5, 1, gold.s)
    for (x, y), c in {(7, 7): skin.s, (8, 7): skin.l, (7, 8): skin.m, (8, 8): skin.d}.items():   # chest gem
        s.set(x, y, c)
    for x, y in ((7, 9), (8, 9)):
        s.set(x, y, gold.d)
    return s


def apple(enchanted: bool = False) -> Sprite:
    body = _disc_cells(8, 9.8, 5.6)
    body -= {(8, 4), (7, 4)}                           # dimple at the top
    s = shaded(body, theme.GOLD)
    s.set(5, 7, theme.GOLD.s)
    s.set(6, 6, theme.GOLD.s)
    s.set(5, 8, theme.GOLD.l)
    # stem + leaf
    for x, y in ((8, 3), (8, 2)):
        s.set(x, y, "#6a4420")
    for x, y in ((9, 2), (10, 2), (10, 3)):
        s.set(x, y, "#4fbf3a" if (x, y) != (10, 3) else "#2f8f2a")
    outline = theme.INK
    if enchanted:
        outline = "#7a35e0"
        for x, y in ((3, 5), (13, 6), (11, 14), (2, 11)):
            s.set(x, y, "#f0d8ff")
    s.outline(outline)
    if enchanted:                                      # sparkle crosses just outside the outline
        for cx, cy in ((2, 4), (13, 5)):
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                if not s.solid(cx + dx, cy + dy):
                    s.set(cx + dx, cy + dy, "#e6c8ff" if (dx, dy) != (0, 0) else "#ffffff")
    return s


def ender_pearl() -> Sprite:
    ramp = Ramp("#0a3640", "#17766f", "#3ec7ad", "#c8fff0")
    body = _disc_cells(8, 8, 5.4)
    s = shaded(body, ramp)
    for x, y in ((4, 7), (5, 8), (6, 9), (7, 10), (8, 11), (8, 5), (9, 6), (10, 7), (11, 8)):   # two dark bands
        if (x, y) in body:
            s.set(x, y, ramp.d)
    for x, y in ((5, 5), (6, 4), (5, 6), (7, 4)):
        s.set(x, y, ramp.s)
    s.set(6, 5, ramp.l)
    s.set(9, 9, ramp.l)
    s.outline(theme.INK)
    return s


def end_crystal() -> Sprite:
    pink = Ramp("#5d1a86", "#b247dc", "#ec8bff", "#ffe7ff")
    rows = [
        "................",
        ".......BB.......",
        "......BBBB......",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "...BBBBBBBBBB...",
        "...BBBBBBBBBB...",
        "...BBBBBBBBBB...",
        "....BBBBBBBB....",
        ".....BBBBBB.....",
        "......BBBB......",
        ".......BB.......",
        "................",
        "................",
        "................",
        "................",
    ]
    cells = _cells(rows)
    s = Sprite(16, 16)
    # shift down so the gem is centred vertically
    for (x, y) in cells:
        yy = y + 2
        top = y <= 5
        left = x <= 7
        if top and left:
            c = pink.l
        elif top:
            c = pink.m
        elif left:
            c = pink.m
        else:
            c = pink.d
        if x in (7, 8) and 3 <= y <= 9:                   # centre ridge
            c = pink.s if x == 7 else pink.l
        s.set(x, yy, c)
    s.set(5, 6, "#ffffff")
    s.set(4, 7, pink.s)
    s.outline(theme.INK)
    return s


def exp_bottle() -> Sprite:
    glass = "#cfe9f4"
    liquid = Ramp("#2f8f18", "#78dc34", "#bfff62", "#f3ffc6")
    body = _disc_cells(8, 10.2, 5.0)
    inner = _disc_cells(8, 10.2, 3.7)
    s = Sprite(16, 16)
    for x, y in body - inner:
        s.set(x, y, glass)
    shaded(inner, liquid, s)
    for x, y in ((7, 4), (8, 4), (7, 5), (8, 5)):         # neck
        s.set(x, y, glass)
    s.set(7, 5, liquid.l)
    s.set(8, 5, liquid.m)
    for x, y in ((7, 2), (8, 2), (7, 3), (8, 3)):         # cork
        s.set(x, y, "#a8743a" if x == 7 else "#7e5226")
    for x, y in ((6, 8), (5, 9)):
        s.set(x, y, "#ffffff")
    for x, y in ((9, 11), (7, 12), (10, 9)):              # bubbles
        s.set(x, y, liquid.s)
    s.outline(theme.INK)
    return s


# potion bottles share one liquid mask so the tinted overlay lines up on all three variants
_POTION_SILHOUETTE = (
    {(x, 3) for x in range(6, 10)} | {(x, 4) for x in range(6, 10)} | {(x, 5) for x in range(6, 10)}
    | {(x, 6) for x in range(5, 11)} | {(x, 7) for x in range(4, 12)}
    | {(x, y) for y in range(8, 13) for x in range(3, 13)}
    | {(x, 13) for x in range(4, 12)} | {(x, 14) for x in range(5, 11)}
)


def _potion_parts():
    full = _POTION_SILHOUETTE
    interior = {(x, y) for (x, y) in full
                if all(n in full for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))}
    liquid = {(x, y) for (x, y) in interior if y >= 6}
    rim = full - liquid - {(7, 3), (8, 3), (7, 4), (8, 4), (7, 5), (8, 5)}     # neck interior stays transparent
    return liquid, rim


def potion_overlay() -> Sprite:
    liquid, _ = _potion_parts()
    s = Sprite(16, 16)
    for x, y in liquid:
        g = 255 - 10 * max(0, y - 6) - (14 if x > 9 else 0)
        s.set(x, y, (g, g, g, 255))
    for x, y in ((5, 8), (5, 9), (6, 8)):                  # glint stays bright after tinting
        if (x, y) in liquid:
            s.set(x, y, (255, 255, 255, 255))
    return s


def potion_bottle(kind: str = "potion") -> Sprite:
    liquid, rim = _potion_parts()
    s = Sprite(16, 16)
    glass = {"potion": "#d6ebf6", "splash": "#eaf6ff", "lingering": "#d7c6ee"}[kind]
    shade = {"potion": "#9fc3d6", "splash": "#b8d4e8", "lingering": "#a58fc9"}[kind]
    for x, y in rim:
        s.set(x, y, glass if (x + y) < 13 else shade)
    cork = {"potion": ("#a8743a", "#7e5226"), "splash": ("#e8f4ff", "#9ab8d0"), "lingering": ("#b06be0", "#7a3fb0")}[kind]
    for x, y in ((6, 1), (7, 1), (8, 1), (9, 1), (6, 2), (7, 2), (8, 2), (9, 2)):
        s.set(x, y, cork[0] if y == 1 or x < 8 else cork[1])
    for x, y in ((5, 8), (5, 9), (4, 9)):
        if (x, y) in rim:
            s.set(x, y, "#ffffff")
    s.outline(theme.INK)
    if kind == "splash":                                    # wisps of vapour show it is a throwable
        for x, y in ((3, 2), (12, 3), (13, 5)):
            s.set(x, y, "#dff2ff")
    if kind == "lingering":
        for x, y in ((3, 2), (12, 3), (13, 5)):
            s.set(x, y, "#d9a8ff")
    return s


# --------------------------------------------------------------------------- bow + arrow
def _bezier(p0, c, p1, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * c[0] + t ** 2 * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * c[1] + t ** 2 * p1[1]
        pts.append((t, x, y))
    return pts


def bow(pull: int = -1) -> Sprite:
    """pull = -1: relaxed; 0..2: increasingly drawn with an arrow nocked."""
    wood = Ramp("#4a2e12", "#6f4721", "#9a6a35", "#c79656")
    s = Sprite(16, 16)
    a, b = (12.5, 3.5), (3.5, 12.5)
    limb = set()
    grip = set()
    for t, x, y in _bezier(a, (0.8, 0.8), b):
        cell = (int(x), int(y))
        (grip if 0.40 <= t <= 0.60 else limb).add(cell)
        for nb in ((cell[0] + 1, cell[1]), (cell[0], cell[1] + 1)):          # 2px thick towards the string
            if 0.08 <= t <= 0.92:
                (grip if 0.40 <= t <= 0.60 else limb).add(nb)
    limb -= grip
    solid = limb | grip
    for x, y in limb:
        s.set(x, y, shade_part(x, y, solid, wood))
    for x, y in grip:
        s.set(x, y, "#2c1a0c" if (x + y) % 2 else "#4a2f18")                  # leather wrap
    # string
    string = "#e9eef2"
    d = {-1: 0.0, 0: 1.6, 1: 2.8, 2: 4.0}[pull]
    n = (7.5 + d, 7.5 + d)
    s.line(13, 3, round(n[0]), round(n[1]), string)
    s.line(3, 13, round(n[0]), round(n[1]), string)
    if pull >= 0:
        # arrow points to the upper-left, nocked at the string, through the bow
        nock = (round(n[0]), round(n[1]))
        s.line(nock[0] - 1, nock[1] - 1, 4, 4, "#d9b878")                       # shaft (lighter than the limbs)
        s.points([(3, 3), (3, 2), (2, 3), (4, 3), (3, 4)], "#c4d0da")            # head
        s.set(2, 2, "#ffffff")
        s.set(3, 3, "#eef4f8")
        s.points([(nock[0] - 1, nock[1] - 2), (nock[0] - 2, nock[1] - 1)], "#f4f8fb")     # fletching
        s.points([(nock[0], nock[1] - 1), (nock[0] - 1, nock[1])], "#aeb9c4")
    s.outline(theme.INK)
    return s


def arrow() -> Sprite:
    s = Sprite(16, 16)
    shaft = Ramp("#5a3a18", "#8a5f2c", "#b88848", "#d8ad6e")
    for i, (x, y) in enumerate(((11, 4), (10, 5), (9, 6), (8, 7), (7, 8), (6, 9), (5, 10), (4, 11))):
        s.set(x, y, shaft.l if i % 3 == 0 else shaft.m)
    head = [(14, 1), (13, 2), (12, 3), (12, 2), (13, 3)]
    for x, y in head:
        s.set(x, y, "#c8d3dc")
    s.set(14, 1, "#ffffff")
    s.set(13, 2, "#eaf1f6")
    s.set(13, 3, "#8fa0ae")
    s.set(12, 3, "#8fa0ae")
    for x, y in ((3, 12), (2, 13), (3, 11), (4, 12), (2, 12), (3, 13)):   # fletching
        s.set(x, y, "#f4f8fb")
    for x, y in ((3, 12), (2, 13)):
        s.set(x, y, "#aeb9c4")
    s.outline(theme.INK)
    return s


# --------------------------------------------------------------------------- generate
def generate(pack) -> None:
    kinds = {"sword": SWORD, "pickaxe": PICKAXE, "axe": AXE, "shovel": SHOVEL, "hoe": HOE, "spear": SPEAR}
    for material in MATERIAL_ORDER:
        for kind, rows in kinds.items():
            glint = SWORD_GLINT if kind == "sword" else ()
            pack.png(f"{ITEM}/{material}_{kind}.png", tool(rows, material, extra_shine=glint))
        pack.png(f"{ITEM}/{material}_spear_in_hand.png", spear_in_hand(material))
    pieces = {"helmet": HELMET, "chestplate": CHESTPLATE, "leggings": LEGGINGS, "boots": BOOTS}
    for material in ARMOR_ORDER:
        for piece, rows in pieces.items():
            pack.png(f"{ITEM}/{material}_{piece}.png", armor_piece(rows, material))
    pack.png(f"{ITEM}/mace.png", render_mask(MACE, {"B": Ramp("#3a3442", "#615a6e", "#8f87a0", "#cbc4dc"),
                                                    "S": Ramp("#2a2530", "#46404f", "#6a6377", "#9b94ad"),
                                                    "H": HANDLE}, shine=[(11, 3)]))
    pack.png(f"{ITEM}/totem_of_undying.png", totem())
    pack.png(f"{ITEM}/golden_apple.png", apple())
    pack.png(f"{ITEM}/enchanted_golden_apple.png", apple(enchanted=True))
    pack.png(f"{ITEM}/ender_pearl.png", ender_pearl())
    pack.png(f"{ITEM}/end_crystal.png", end_crystal())
    pack.png(f"{ITEM}/experience_bottle.png", exp_bottle())
    pack.png(f"{ITEM}/potion_overlay.png", potion_overlay())
    pack.png(f"{ITEM}/potion.png", potion_bottle("potion"))
    pack.png(f"{ITEM}/splash_potion.png", potion_bottle("splash"))
    pack.png(f"{ITEM}/lingering_potion.png", potion_bottle("lingering"))
    pack.png(f"{ITEM}/bow.png", bow(-1))
    for i in range(3):
        pack.png(f"{ITEM}/bow_pulling_{i}.png", bow(i))
    pack.png(f"{ITEM}/arrow.png", arrow())
