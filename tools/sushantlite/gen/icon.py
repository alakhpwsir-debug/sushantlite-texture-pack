"""pack.png -- 256x256 pack icon: crossed swords over a night-blue gradient, with a pixel wordmark.

Drawn on a 64x64 grid and enlarged 4x with nearest-neighbour so it stays crisp pixel art.
"""
from __future__ import annotations

import math

from PIL import Image

from .. import theme
from ..sprite import Sprite, mix, rgba
from . import items

# 5x7 pixel glyphs for the letters in the wordmark
GLYPHS = {
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
}


def _text(s: Sprite, word: str, x: int, y: int, colour, shadow=None, scale: int = 1) -> int:
    """Draw ``word`` at (x, y); returns the width drawn."""
    cx = x
    for ch in word:
        glyph = GLYPHS[ch]
        for gy, row in enumerate(glyph):
            for gx, c in enumerate(row):
                if c == "#":
                    for dx in range(scale):
                        for dy in range(scale):
                            if shadow:
                                s.set(cx + gx * scale + dx + 1, y + gy * scale + dy + 1, shadow)
                            s.set(cx + gx * scale + dx, y + gy * scale + dy, colour)
        cx += (5 + 1) * scale
    return cx - x - scale


def _text_width(word: str, scale: int = 1) -> int:
    return len(word) * 6 * scale - scale


def build() -> Image.Image:
    W = 64
    s = Sprite(W, W)
    # background: vertical gradient with a cyan glow rising from the bottom-left
    for y in range(W):
        for x in range(W):
            t = y / (W - 1)
            base = mix("#101b32", "#070b15", t)
            d = math.hypot(x - 6, y - 58) / 54
            glow = max(0.0, 1 - d) ** 2
            s.set(x, y, mix(base, theme.ACCENT_DARK, glow * 0.55))
    # border
    s.frame(0, 0, W, W, "#0a1020")
    s.frame(1, 1, W - 2, W - 2, mix(theme.PANEL_EDGE, "#0a1020", 0.35))

    # crossed swords: diamond (left-leaning) + netherite (mirrored), 16x16 -> 2x
    dia = items.tool(items.SWORD, "diamond")
    net = items.tool(items.SWORD, "netherite").flip_h()

    def scaled(sp: Sprite, k: int) -> Sprite:
        out = Sprite(sp.w * k, sp.h * k)
        for y in range(sp.h):
            for x in range(sp.w):
                p = sp.px[y][x]
                if p is not None:
                    out.rect(x * k, y * k, k, k, p)
        return out

    big_net = scaled(net, 2)
    big_dia = scaled(dia, 2)
    s.blit(big_net, 16, 2)
    s.blit(big_dia, 16, 2)

    # wordmark
    sushant_w = _text_width("SUSHANT")
    _text(s, "SUSHANT", (W - sushant_w) // 2, 39, "#f4fbff", shadow="#0a1020")
    lite_w = _text_width("LITE", 2)
    _text(s, "LITE", (W - lite_w) // 2, 49, theme.ACCENT, shadow="#0a3a4c", scale=2)
    return s.to_image(4)


def generate(pack) -> None:
    pack.png("pack.png", build())
