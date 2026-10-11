"""Sun, moon phases and clouds.

Sun and moon textures are drawn on opaque black: the game composites them with an
additive blend, so black adds nothing.  Everything is original art.
"""
from __future__ import annotations

import math

from .. import noise, theme
from ..sprite import Sprite, blank, mix

CEL = "assets/minecraft/textures/environment/celestial"


def _glow(s: Sprite, cx: float, cy: float, radius: float, rgb: tuple[int, int, int], strength: float, power: float = 2.4):
    for y in range(s.h):
        for x in range(s.w):
            r = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            g = max(0.0, 1 - r / radius) ** power * strength
            if g > 0:
                base = s.get(x, y) or (0, 0, 0, 255)
                s.set(x, y, tuple(min(255, round(base[i] + rgb[i] * g)) for i in range(3)) + (255,))


def sun() -> Sprite:
    s = Sprite(32, 32).fill((0, 0, 0, 255))
    _glow(s, 16, 16, 15.5, (255, 214, 110), 0.46)
    s.rect(11, 11, 10, 10, "#f2a81c")                    # amber rim
    s.rect(12, 12, 8, 8, "#ffd447")
    s.rect(13, 13, 6, 6, "#fff0a0")
    s.rect(14, 14, 4, 4, "#fffce8")
    for x, y in ((11, 11), (20, 11), (11, 20), (20, 20)):   # soften the corners
        s.set(x, y, (60, 44, 12, 255))
    return s


_MOON_K = {          # terminator position (1 = new, 0 = quarter, -1 = full) and which side is lit
    "new_moon": (1.0, "r"),
    "waxing_crescent": (0.55, "r"),
    "first_quarter": (0.0, "r"),
    "waxing_gibbous": (-0.55, "r"),
    "full_moon": (-1.0, "r"),
    "waning_gibbous": (-0.55, "l"),
    "third_quarter": (0.0, "l"),
    "waning_crescent": (0.55, "l"),
}
_CRATERS = {(14, 13), (15, 14), (19, 15), (18, 19), (13, 18), (20, 18), (16, 21), (17, 12), (12, 15)}


def moon(phase: str) -> Sprite:
    k, side = _MOON_K[phase]
    s = Sprite(32, 32).fill((0, 0, 0, 255))
    illum = (1 - k) / 2
    _glow(s, 16, 16, 14, (110, 140, 210), 0.20 * (0.25 + illum), power=2.6)
    R = 5.3
    for y in range(32):
        for x in range(32):
            u = (x + 0.5 - 16) / R
            v = (y + 0.5 - 16) / R
            if u * u + v * v > 1:
                continue
            w = math.sqrt(max(0.0, 1 - v * v))
            lit = (u > k * w) if side == "r" else (u < -k * w)
            if lit and phase != "new_moon":
                c = (214, 226, 248)
                if (x, y) in _CRATERS:
                    c = (160, 176, 206)
                if u * u + v * v > 0.72:                  # slight limb darkening
                    c = tuple(int(ch * 0.9) for ch in c)
                if u < -0.3 and v < -0.2 and (x, y) not in _CRATERS:
                    c = (240, 246, 255)
                s.set(x, y, c + (255,))
            else:
                s.set(x, y, (22, 27, 40, 255))
    return s


def clouds(pack) -> None:
    n = noise.fractal(256, [(8, 0.52), (16, 0.30), (32, 0.18)], seed=7)
    t = noise.quantile(n, 0.77)          # ~23 % coverage (vanilla is ~28 %): a lighter sky
    s = Sprite(256, 256)
    for y in range(256):
        for x in range(256):
            if n[y][x] > t:
                s.set(x, y, (255, 255, 255, 255))
    pack.png("assets/minecraft/textures/environment/clouds.png", s)


def generate(pack) -> None:
    pack.png(f"{CEL}/sun.png", sun())
    for phase in _MOON_K:
        pack.png(f"{CEL}/moon/{phase}.png", moon(phase))
    clouds(pack)
