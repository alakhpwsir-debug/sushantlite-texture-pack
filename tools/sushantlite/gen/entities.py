"""Entity skins: arrows, trident, XP orbs, fishing bobber, end crystal.

Several of these textures moved in 26.1, so the shared base layer only holds the ones that did not
(``arrow``, ``end_crystal``); the rest are written twice, into ``overlay_1_21_11`` (formats 75-83)
and ``overlay_26_1`` (84+):

    1.21.11                                  26.1 and newer
    entity/trident.png                       entity/trident/trident.png
    entity/experience_orb.png                entity/experience/experience_orb.png
    entity/fishing_hook.png                  entity/fishing/fishing_hook.png
    entity/projectiles/tipped_arrow.png      entity/projectiles/arrow_tipped.png
    entity/projectiles/spectral_arrow.png    entity/projectiles/arrow_spectral.png

UV layouts come from the models' cuboids (see ``uv.py``); for the arrow, XP orb and bobber the
vanilla textures were only inspected to learn which cells the renderer samples.

* arrow / tipped arrow  32x32  two crossed 16x5 quads (left half = one side, right half = the same
  drawing mirrored) plus a 5x5 '+' for the tail cap.  The potion colour is *multiplied* over the
  tipped texture, so it is kept white/grey and cyan is reserved for the plain arrow.
* trident               32x32  pole 1x25x1, cross-piece 3x2x1, three 1x4x1 prongs.
* XP orb                64x64  4x4 cells of 16x16; cell n is the orb for value bracket n (0-10).  The
  renderer tints the texture lime/yellow, so it is grey -- and every disc is drawn ~38 % smaller than
  vanilla's to cut screen clutter while keeping the size progression.
* fishing bobber        8x8
* end crystal           128x64 for a 64x32 model (UV scale 2): outer + inner glass share (0,0), the
  core cube is at (64,0) and the base slab at (0,32).
"""
from __future__ import annotations

import math

from .. import theme
from ..sprite import Sprite, mix, rgba
from ..theme import Ramp
from ..uv import box_faces, paint

TEX = "assets/minecraft/textures/entity"
LEGACY, MODERN = "overlay_1_21_11", "overlay_26_1"


def both(pack, legacy_rel: str, modern_rel: str, art) -> None:
    """Write ``art`` to the 1.21.11 path (legacy overlay) and the 26.1+ path (modern overlay)."""
    pack.png(f"{TEX}/{legacy_rel}", art, overlay=LEGACY)
    pack.png(f"{TEX}/{modern_rel}", art, overlay=MODERN)


# --------------------------------------------------------------------------- arrows
# left half of the 16x5 strip (x 0..15, y 0..4); the right half is the mirror image (x -> 31 - x)
FEATHER_TOP = {(0, 0): 0, (1, 0): 1, (2, 0): 2, (1, 1): 0, (2, 1): 1, (3, 1): 2}      # value = shade index
FEATHER_BOTTOM = {(1, 3): 0, (2, 3): 1, (3, 3): 2, (0, 4): 0, (1, 4): 1, (2, 4): 2}
HEAD_BUMPS_TOP = [(13, 1), (14, 1)]
HEAD_BUMPS_BOTTOM = [(13, 3), (14, 3)]


class ArrowPalette:
    def __init__(self, nock, shaft, collar, head, bump_top, bump_bottom, vane_top, vane_bottom, cap_bar, cap_cross, cap_mid):
        self.nock, self.shaft, self.collar, self.head = nock, shaft, collar, head
        self.bump_top, self.bump_bottom = bump_top, bump_bottom
        self.vane_top, self.vane_bottom = vane_top, vane_bottom
        self.cap_bar, self.cap_cross, self.cap_mid = cap_bar, cap_cross, cap_mid


ARROW = ArrowPalette(
    nock="#8a6a3a", shaft=("#e6cc96", "#d2b37a"), collar="#6f7f90",
    head=("#9fb0bd", "#d0dde6", "#ffffff"), bump_top=("#b8c8d4", "#e8f1f7"), bump_bottom=("#8796a3", "#8796a3"),
    vane_top=("#9aa6b2", "#dfe6ec", "#ffffff"),
    vane_bottom=("#dfe6ec", "#ffffff", "#dfe6ec"),
    cap_bar="#cfd8e2", cap_cross="#f4fbff", cap_mid="#ffffff")

# tint-friendly: neutral whites and greys only (the potion colour is multiplied over this)
TIPPED = ArrowPalette(
    nock="#b5b5b5", shaft=("#f2f2f2", "#d9d9d9"), collar="#9a9a9a",
    head=("#c4c4c4", "#efefef", "#ffffff"), bump_top=("#d8d8d8", "#f6f6f6"), bump_bottom=("#b0b0b0", "#b0b0b0"),
    vane_top=("#dedede", "#ffffff", "#dedede"), vane_bottom=("#dedede", "#ffffff", "#dedede"),
    cap_bar="#ffffff", cap_cross="#ececec", cap_mid="#ffffff")

SPECTRAL = ArrowPalette(
    nock="#a8641a", shaft=("#ffd54a", "#e6b02a"), collar="#a8641a",
    head=("#fff0a0", "#fff8c8", "#ffffff"), bump_top=("#fff0a0", "#fff8c8"), bump_bottom=("#e6b02a", "#e6b02a"),
    vane_top=("#e6b02a", "#ffe14d", "#fff08a"), vane_bottom=("#e6b02a", "#ffe14d", "#fff08a"),
    cap_bar="#ffe14d", cap_cross="#fff8c8", cap_mid="#ffffff")


def arrow_texture(p: ArrowPalette) -> Sprite:
    s = Sprite(32, 32)

    def put(x: int, y: int, colour) -> None:
        s.set(x, y, colour)
        s.set(31 - x, y, colour)               # the right half mirrors the left

    for (x, y), shade in FEATHER_TOP.items():
        put(x, y, p.vane_top[shade])
    for (x, y), shade in FEATHER_BOTTOM.items():
        put(x, y, p.vane_bottom[shade])
    for x in range(0, 2):
        put(x, 2, p.nock)
    for x in range(2, 12):
        put(x, 2, p.shaft[1] if x % 3 == 0 else p.shaft[0])
    put(12, 2, p.collar)
    for i, x in enumerate((13, 14, 15)):
        put(x, 2, p.head[i])
    for i, (x, y) in enumerate(HEAD_BUMPS_TOP):
        put(x, y, p.bump_top[i])
    for i, (x, y) in enumerate(HEAD_BUMPS_BOTTOM):
        put(x, y, p.bump_bottom[i])
    # tail cap: a '+' on each of the two 5x5 faces at (0,5) and (5,5)
    for ox in (0, 5):
        for k in range(5):
            s.set(ox + 2, 5 + k, p.cap_bar)                   # vertical bar
            s.set(ox + k, 7, p.cap_cross)                     # horizontal bar
        s.set(ox + 2, 7, p.cap_mid)
    return s


# --------------------------------------------------------------------------- trident
NAVY = theme.NAVY


def _prong(ly: int, face: str):
    tip = ("#e4fffb", theme.ACCENT_LIGHT, theme.ACCENT, theme.ACCENT_DARK)[ly]
    return mix(tip, "#0b1a2c", 0.30) if face in ("west", "east") else tip


def trident_texture() -> Sprite:
    s = Sprite(32, 32)

    # three prongs: the middle one at texOffs(0,0); the two outer ones share texOffs(4,3)
    for origin in ((0, 0), (4, 3)):
        faces = box_faces(origin[0], origin[1], 1, 4, 1)
        for name, (x, y, w, h) in faces.items():
            for ly in range(h):
                for lx in range(w):
                    if name in ("top", "bottom"):
                        s.set(x + lx, y + ly, "#ffffff" if name == "top" else theme.ACCENT_DARK)
                    else:
                        s.set(x + lx, y + ly, _prong(ly, name))

    # cross-piece 3x2x1 at texOffs(4,0)
    for name, (x, y, w, h) in box_faces(4, 0, 3, 2, 1).items():
        def cross(lx, ly, name=name, w=w, h=h):
            if name in ("west", "east"):
                return NAVY.d
            if name in ("top", "bottom"):
                return NAVY.l if name == "top" else NAVY.d
            if name == "front" and lx == w // 2 and ly == 0:
                return NAVY.s                                         # centre stud
            return NAVY.l if ly == 0 else NAVY.m if name == "front" else NAVY.d
        paint(s, (x, y, w, h), cross)

    # pole 1x25x1 at texOffs(0,6)
    for name, (x, y, w, h) in box_faces(0, 6, 1, 25, 1).items():
        def pole(lx, ly, name=name, h=h):
            if name == "top":
                return NAVY.l
            if name == "bottom":
                return NAVY.d
            base = {"front": NAVY.m, "back": NAVY.m, "west": NAVY.d, "east": NAVY.d}[name]
            if ly in (6, 7, 18, 19):                                  # cyan glow rings
                return (theme.ACCENT if ly in (6, 18) else theme.ACCENT_DARK) if name == "front" else mix(base, theme.ACCENT_DARK, 0.5)
            if ly % 6 == 0:                                           # leather wrap bands
                return NAVY.l if name == "front" else base
            if ly >= h - 2:
                return NAVY.s if name == "front" else NAVY.l          # butt cap
            return base
        paint(s, (x, y, w, h), pole)
    return s


# --------------------------------------------------------------------------- XP orb
ORB_RADII = [2.7, 3.3, 3.8, 3.8, 3.8, 4.3, 4.3, 4.3, 5.2, 5.2, 5.2]      # cells 0-10 (~62 % of vanilla's 4.4-8.4)


def orb_cell(r: float) -> Sprite:
    c = Sprite(16, 16)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if d > r:
                continue
            if r < 2.3:
                c.set(x, y, "#8a8a8a" if d > r - 0.9 else "#ffffff")
            elif d > r - 0.9:
                c.set(x, y, "#7c7c7c")
            elif d > r - 1.8:
                c.set(x, y, "#c4c4c4")
            else:
                c.set(x, y, "#ffffff")
    return c


def xp_orb_texture() -> Sprite:
    s = Sprite(64, 64)
    for i in range(16):                                   # cells 11-15 are unused by the game; keep them sane
        r = ORB_RADII[i] if i < len(ORB_RADII) else ORB_RADII[2]
        s.blit(orb_cell(r), (i % 4) * 16, (i // 4) * 16)
    return s


# --------------------------------------------------------------------------- fishing bobber
def bobber_texture() -> Sprite:
    s = Sprite(8, 8)
    for x, colour in ((3, "#ff3b52"), (4, "#ff6b7c"), (5, "#d6203b")):          # red cap
        s.set(x, 1, colour)
    for x in (3, 4, 5):
        s.set(x, 2, "#f4fbff" if x != 5 else "#c9d6e0")                           # white body
        s.set(x, 3, "#e3ebf2" if x != 5 else "#b3c2cf")                           # lower half of the float
    for y in (4, 5, 6):
        s.set(4, y, "#dfe9f0")                                                    # line
    s.set(3, 7, "#aebcc8")
    s.set(4, 7, "#dfe9f0")
    s.set(2, 6, "#aebcc8")                                                        # hook barb
    return s


# --------------------------------------------------------------------------- end crystal (128x64)
CRYSTAL = Ramp("#5d1a86", "#b247dc", "#ec8bff", "#ffe7ff")      # the core stays magenta
FRAME = "#2fc8ec"                                               # glass edge: saturated cyan
FRAME_CAP = "#d4f9ff"                                           # brighter corner caps
GLASS = box_faces(0, 0, 8, 8, 8, scale=2)           # outer and inner glass share this patch
CORE = box_faces(32, 0, 8, 8, 8, scale=2)
BASE = box_faces(0, 16, 12, 4, 12, scale=2)


def glass_face(lx: int, ly: int):
    """16x16 pane: a 1px cyan frame, L-shaped near-white caps in the corners, a small glint; the rest is clear."""
    edge = lx in (0, 15) or ly in (0, 15)
    ix, iy = min(lx, 15 - lx), min(ly, 15 - ly)         # distance to the nearest vertical / horizontal edge
    if (ix <= 1 and iy <= 4) or (iy <= 1 and ix <= 4):
        return FRAME_CAP                                # corner cap (2 px thick, 5 px long)
    if edge:
        return FRAME
    if (lx, ly) in ((3, 3), (4, 4), (5, 5), (3, 4), (4, 3)):        # glint
        return "#ffffff"
    return None


def core_face(top: bool, bottom: bool):
    def fn(lx: int, ly: int):
        ring = max(abs(lx - 7.5), abs(ly - 7.5))                     # Chebyshev distance: square rings
        if ring < 2.0:
            c = CRYSTAL.s
        elif ring < 4.0:
            c = CRYSTAL.l
        elif ring < 6.0:
            c = CRYSTAL.m
        else:
            c = CRYSTAL.d
        if top:
            c = mix(c, "#ffffff", 0.12)
        if bottom:
            c = mix(c, "#2a0a44", 0.25)
        if (lx + ly) % 4 == 0 and ring >= 2:                         # faceting
            c = mix(c, CRYSTAL.d, 0.18)
        return c
    return fn


def base_face(name: str):
    def fn(lx: int, ly: int):
        if name in ("top", "bottom"):
            w = 24
            edge = min(lx, ly, w - 1 - lx, w - 1 - ly)
            if name == "bottom":
                return "#10151f"
            if edge == 0:
                return "#0c101a"
            if edge == 1:
                return theme.ACCENT_DARK                             # glowing inlay line
            if edge in (2, 3):
                return "#232c42"
            return "#1a2133" if (lx * 7 + ly * 3) % 11 else "#2a3550"
        # sides: 24 x 8
        if ly == 0:
            return theme.ACCENT_DARK
        if ly == 1:
            return "#2e3b5c"
        if lx % 6 == 3 and ly in (3, 4):
            return "#6b7fae"                                          # rivets
        return "#202840" if ly < 6 else "#161c2e"
    return fn


def crystal_texture() -> Sprite:
    s = Sprite(128, 64)
    for rect in GLASS.values():
        paint(s, rect, glass_face)
    for name, rect in CORE.items():
        paint(s, rect, core_face(name == "top", name == "bottom"))
    for name, rect in BASE.items():
        paint(s, rect, base_face(name))
    return s


# --------------------------------------------------------------------------- generate
def generate(pack) -> None:
    pack.png(f"{TEX}/projectiles/arrow.png", arrow_texture(ARROW))
    tipped, spectral = arrow_texture(TIPPED), arrow_texture(SPECTRAL)
    both(pack, "projectiles/tipped_arrow.png", "projectiles/arrow_tipped.png", tipped)
    both(pack, "projectiles/spectral_arrow.png", "projectiles/arrow_spectral.png", spectral)
    both(pack, "trident.png", "trident/trident.png", trident_texture())
    both(pack, "experience_orb.png", "experience/experience_orb.png", xp_orb_texture())
    both(pack, "fishing_hook.png", "fishing/fishing_hook.png", bobber_texture())
    pack.png(f"{TEX}/end_crystal/end_crystal.png", crystal_texture())
