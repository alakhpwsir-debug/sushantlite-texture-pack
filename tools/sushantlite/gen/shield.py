"""Shield skin -- the first asset that needs the per-version overlays.

Vanilla moved the two base shield textures in 26.1:

    1.21.11    textures/entity/shield_base.png          (+ _nopattern)
    26.1+      textures/entity/shield/shield_base.png   (+ _nopattern)

so the same artwork is written to ``overlay_1_21_11`` (formats 75-83) and
``overlay_26_1`` (formats 84+); the shared base layer stays clean.

UV layout (derived from the model's two cuboids and checked against the vanilla
texture: all 716 opaque pixels match exactly)::

    plate  texOffs(0, 0)   box 12 x 22 x 1   front face = (1, 1) 12x22 (banner patterns fill its
                                             10x20 interior and leave a 1px rim), back face = (14, 1)
    handle texOffs(26, 0)  box  2 x  6 x 6

``shield_base`` is tinted with the banner colour, so its face is near-white;
``shield_base_nopattern`` (plain shield) carries the full SushantLite design.
"""
from __future__ import annotations

from .. import theme
from ..sprite import Sprite, mix, rgba
from ..uv import box_faces, paint


PLATE = box_faces(0, 0, 12, 22, 1)
HANDLE = box_faces(26, 0, 2, 6, 6)


def lerp_rows(top: str, bottom: str, h: int):
    return lambda x, y: mix(top, bottom, y / max(1, h - 1))


# --------------------------------------------------------------------------- faces
def front_plain(x: int, y: int):
    """12x22 front: navy steel plate, bright cyan rim, cyan gem emblem, rivets."""
    rim = x in (0, 11) or y in (0, 21)
    if rim:
        return theme.ACCENT if (x in (0, 11) and 0 < y < 21) or y in (0, 21) else theme.ACCENT_DARK
    ix, iy = x - 1, y - 1                                   # interior 10 x 20
    if (ix, iy) in ((0, 0), (9, 0), (0, 19), (9, 19)):      # rivets
        return "#b4c4e0"
    dx, dy = ix - 4.5, iy - 9.5
    steel = mix("#56699a", "#26314c", iy / 19)
    gem = abs(dx) / 4.3 + abs(dy) / 6.6
    if gem <= 1.0:
        if gem > 0.84:
            return "#0b1a2c"                                 # dark gem outline
        if dx < -0.4 and dy < 0.6:
            return theme.ACCENT_LIGHT                        # lit facet
        if dx > 0.4 and dy > 0.4:
            return theme.ACCENT_DARK                         # shadow facet
        return theme.ACCENT
    # engraved chevron lines either side of the gem
    if abs(dx) <= 4.5 and (iy in (3, 16)) and abs(dx) > 2.2:
        return mix(steel, "#9fb2d6", 0.35)
    return steel


def front_tintable(x: int, y: int):
    """Near-white face so the banner colour tints it; neutral grey rim."""
    rim = x in (0, 11) or y in (0, 21)
    if rim:
        return "#b9bcc7" if (x == 0 or y == 0) else "#9a9eab"
    return mix("#f4f4f4", "#dcdce0", (y - 1) / 19)


def back_face(x: int, y: int):
    """Inside of the shield: dark planks, a leather strap with a cyan stud."""
    rim = x in (0, 11) or y in (0, 21)
    if rim:
        return "#2a1b0d"
    plank = "#51361a" if (y // 5) % 2 == 0 else "#47301a"
    if y % 5 == 0:
        plank = "#2f1e0e"
    if 8 <= y <= 10:
        plank = "#7e5228" if y != 10 else "#5e3d1d"
    if (x, y) in ((5, 9), (6, 9)):
        return theme.ACCENT if x == 5 else theme.ACCENT_DARK
    return plank


def edge(tint: bool):
    base = "#7b7f8d" if tint else "#2d3856"
    shade = "#5f6371" if tint else "#1d263d"
    return lambda x, y: base if (x + y) % 3 else shade


def handle(face: str):
    colours = {"top": "#8b6a40", "bottom": "#3f2a14", "west": "#5d3f20", "east": "#4a3118", "front": "#6f4c26", "back": "#6f4c26"}
    base = colours[face]
    return lambda x, y: mix(base, "#2a1a0c", 0.25) if (x + 2 * y) % 5 == 0 else base


def build(plain: bool) -> Sprite:
    s = Sprite(64, 64)
    paint(s, PLATE["front"], front_plain if plain else front_tintable)
    paint(s, PLATE["back"], back_face)
    for name in ("top", "bottom", "west", "east"):
        paint(s, PLATE[name], edge(not plain))
    for name, rect in HANDLE.items():
        paint(s, rect, handle(name))
    return s


def generate(pack) -> None:
    plain, tint = build(True), build(False)
    legacy = "assets/minecraft/textures/entity"            # 1.21.11
    modern = "assets/minecraft/textures/entity/shield"     # 26.1+
    pack.png(f"{legacy}/shield_base_nopattern.png", plain, overlay="overlay_1_21_11")
    pack.png(f"{legacy}/shield_base.png", tint, overlay="overlay_1_21_11")
    pack.png(f"{modern}/shield_base_nopattern.png", plain, overlay="overlay_26_1")
    pack.png(f"{modern}/shield_base.png", tint, overlay="overlay_26_1")
