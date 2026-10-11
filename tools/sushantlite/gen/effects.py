"""Combat-clarity effects.

* low fire                    -> textures/block/fire_1.png (first-person overlay + world flames)
* no pumpkin overlay          -> textures/misc/pumpkinblur.png
* clear underwater view       -> textures/misc/underwater.png
* clear, see-through water    -> textures/block/water_{still,flow,overlay}.png
* thin rain & snow            -> textures/environment/{rain,snow}.png
* quiet particles             -> explosions, fire/explosion smoke, death puffs and sweep arcs hidden; tiny hit sparks

Everything here is original art generated from code; nothing is derived from
Mojang textures.  Only paths that exist, with identical dimensions, on all
supported versions are written (the validator enforces this).
"""
from __future__ import annotations

import math
import random

from PIL import Image

from .. import theme
from ..sprite import Sprite, blank, rgba, stack_frames, with_alpha

TAU = math.tau


# =============================================================================
# Low fire
# =============================================================================
# How the first-person fire overlay samples fire_1.png (derived from the vanilla render code):
#   * only the central 75 % of each 16x16 frame is mapped (v from 1/8 to 7/8),
#   * the quad is shifted down, so at the default FOV only rows ~2 .. 8.6 are on screen,
#     and at FOV 110 rows ~2 .. 13.
# Vanilla flame tips sit around row 2 (fire fills ~65-79 % of the screen).  Low fire moves the
# tips down to about row 6-7 and lets the flame body fade out below, so the overlay hugs the
# bottom of the screen at every FOV (see docs/previews/low-fire.png for the projection).
FIRE_FRAMES = 32
FIRE_TIP_ROW = 7.0          # average row of the flame tips; raise it for an even lower fire

# colour ramp, tip -> deep body, plus the hot yellow core inside each tongue
_FIRE_RAMP = ["#ffb52e", "#ff9524", "#fb7420", "#ec5a1c", "#d6431a", "#b83319"]
_FIRE_CORE = ["#ffe680", "#ffd24a", "#ffbb33"]

# (centre x, tip lift, flicker amplitude, temporal harmonic, phase, half-width)
_TONGUES = [
    (1.2, 0.0, 0.8, 1, 0.00, 1.9),
    (3.9, 1.1, 0.9, 2, 0.30, 2.2),
    (7.0, 0.7, 0.9, 3, 0.55, 2.4),
    (9.9, 1.1, 0.9, 1, 0.10, 2.1),
    (12.6, 0.6, 0.9, 2, 0.75, 2.3),
    (15.0, 0.1, 0.8, 3, 0.45, 1.8),
]


def _fire_frame(t: int) -> Sprite:
    """One frame of the low-fire strip.  Periodic in ``t`` so the loop is seamless."""
    s = Sprite(16, 16)
    tips = []
    for x in range(16):
        best = 99.0
        for cx, lift, amp, harm, phase, hw in _TONGUES:
            apex = FIRE_TIP_ROW - lift + amp * math.sin(TAU * (harm * t / FIRE_FRAMES + phase))
            best = min(best, apex + 3.4 * (abs(x + 0.5 - cx) / hw) ** 1.2)
        tips.append(max(4.0, min(11.0, best)))
    for x in range(16):
        top = int(round(tips[x]))
        # distance to the nearest tongue centre decides where the yellow core goes
        core_dist = min(abs(x + 0.5 - cx) for cx, *_ in _TONGUES)
        for y in range(top, 16):
            depth = y - top
            colour = _FIRE_RAMP[min(depth, len(_FIRE_RAMP) - 1)]
            if core_dist <= 0.8 and 1 <= depth <= len(_FIRE_CORE):
                colour = _FIRE_CORE[depth - 1]
            elif core_dist <= 1.6 and 1 <= depth <= 2:
                colour = _FIRE_RAMP[max(0, depth - 1)]
            # translucent body: the part below row 9 is only visible with a wide FOV
            alpha = 238 if y <= 9 else 205 if y <= 11 else 150 if y <= 13 else 100
            if depth == 0:
                alpha = min(alpha, 200)
            s.set(x, y, with_alpha(colour, alpha))
    return s


def low_fire(pack) -> None:
    frames = [_fire_frame(t) for t in range(FIRE_FRAMES)]
    # vanilla's fire_1.png.mcmeta is {"animation": {}} (1 tick per frame); keep that speed.
    pack.animated_png("assets/minecraft/textures/block/fire_1.png", stack_frames(frames), {})


# =============================================================================
# Overlays: pumpkin, underwater
# =============================================================================
def overlays(pack) -> None:
    pack.png("assets/minecraft/textures/misc/pumpkinblur.png", blank(256, 256))
    # vanilla keeps `blur` on this texture; harmless for an empty image and keeps behaviour identical
    pack.json("assets/minecraft/textures/misc/pumpkinblur.png.mcmeta", {"texture": {"blur": True}})
    pack.png("assets/minecraft/textures/misc/underwater.png", blank(16, 16))


# =============================================================================
# Clear water
# =============================================================================
def _wave(x: float, y: float, t: float, terms) -> float:
    return sum(a * math.sin(TAU * (kx * x + ky * y + kt * t + ph)) for a, kx, ky, kt, ph in terms)


def clear_water(pack) -> None:
    n = 32
    alpha = 104                     # vanilla is 180 -> noticeably more see-through
    still_terms = [(0.55, 1 / 16, 1 / 16, 1 / n, 0.00), (0.30, 2 / 16, -1 / 16, -2 / n, 0.20),
                   (0.20, -1 / 16, 2 / 16, 1 / n, 0.55)]
    frames = []
    for t in range(n):
        s = Sprite(16, 16)
        for y in range(16):
            for x in range(16):
                v = _wave(x, y, t, still_terms)                   # roughly -1.05 .. 1.05
                g = int(round(188 + 22 * v))
                a = int(round(alpha + 9 * v))
                s.set(x, y, (g, g, min(255, g + 6), a))
        frames.append(s)
    pack.animated_png("assets/minecraft/textures/block/water_still.png", stack_frames(frames), {"frametime": 2})

    flow_terms = [(0.55, 1 / 32, 2 / 32, 1 / n, 0.00), (0.30, 2 / 32, 1 / 32, 0, 0.35),
                  (0.25, -1 / 32, 3 / 32, 2 / n, 0.60)]
    flow = []
    for t in range(n):
        s = Sprite(32, 32)
        for y in range(32):
            for x in range(32):
                v = _wave(x, y, t, flow_terms)                    # y advances 1px/frame -> loops after 32
                g = int(round(184 + 24 * v))
                a = int(round(alpha + 10 * v))
                s.set(x, y, (g, g, min(255, g + 6), a))
        flow.append(s)
    pack.animated_png("assets/minecraft/textures/block/water_flow.png", stack_frames(flow), {})

    ov = Sprite(16, 16).fill((176, 176, 182, alpha))
    pack.png("assets/minecraft/textures/block/water_overlay.png", ov)


# =============================================================================
# Weather
# =============================================================================
def weather(pack) -> None:
    rng = random.Random(0x5115)
    # rain: sparse, short, pale streaks (vanilla: 2.5 % coverage, mean alpha 118, deep blue)
    rain = Sprite(64, 256)
    used_cols: set[int] = set()
    for _ in range(26):
        x = rng.randrange(64)
        while x in used_cols:
            x = rng.randrange(64)
        used_cols.add(x)
        y0 = rng.randrange(256)
        length = rng.randrange(6, 13)
        for i in range(length):
            peak = 1 - abs((i + 0.5) / length - 0.55) * 1.6
            a = int(30 + 62 * max(0.0, peak))
            rain.set(x, (y0 + i) % 256, (176, 204, 250, a))
    pack.png("assets/minecraft/textures/environment/rain.png", rain)

    # snow: fewer, smaller flakes (vanilla: 0.8 % coverage, fully opaque 3x3 crosses)
    snow = Sprite(64, 256)
    for _ in range(26):
        snow.set(rng.randrange(64), rng.randrange(256), (255, 255, 255, 205))
    for _ in range(5):
        x, y = rng.randrange(1, 63), rng.randrange(1, 255)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            snow.set(x + dx, y + dy, (255, 255, 255, 215 if (dx, dy) == (0, 0) else 150))
    pack.png("assets/minecraft/textures/environment/snow.png", snow)


# =============================================================================
# Particles
# =============================================================================
def particles(pack) -> None:
    base = "assets/minecraft/textures/particle"
    # Invisible sprites for particles that have their own artwork:
    #   explosion_*  explosion bursts        big_smoke_*  campfire smoke        sweep_*  sword sweep arcs
    for i in range(16):
        pack.png(f"{base}/explosion_{i}.png", blank(32, 32))
    for i in range(12):
        pack.png(f"{base}/big_smoke_{i}.png", blank(16, 16))
    for i in range(8):
        pack.png(f"{base}/sweep_{i}.png", blank(32, 32))

    # poof (explosion / mob-death puffs), smoke (explosion edges, torches, furnaces) and large_smoke
    # (fire blocks) all share vanilla's generic_* sprites with ~20 other particles (redstone dust, portals,
    # dragon breath, ...), so blanking generic_* would hide far too much.  Instead those three particle
    # definitions are re-pointed at one blank sprite.  The definitions are byte-identical on 1.21.11, 26.1.2,
    # 26.2 and 26.3, and the particle atlas stitches every PNG in textures/particle/.
    pack.png(f"{base}/sushantlite_blank.png", blank(8, 8))
    for name in ("poof", "smoke", "large_smoke"):
        pack.json(f"assets/minecraft/particles/{name}.json", {"textures": ["minecraft:sushantlite_blank"]})

    # Tiny hit sparks: the quad size is fixed by the game, so drawing small art in the middle of
    # the 8x8 sprite makes the particle itself small.
    star = [(3, 2), (4, 2), (2, 3), (3, 3), (4, 3), (5, 3), (2, 4), (3, 4), (4, 4), (5, 4), (3, 5), (4, 5)]
    crit = Sprite(8, 8).points(star, "#e9f6ff")
    crit.points([(3, 3), (4, 3), (3, 4), (4, 4)], "#ffffff")
    pack.png(f"{base}/critical_hit.png", crit)

    ench = Sprite(8, 8).points(star, theme.ACCENT_DARK)
    ench.points([(3, 3), (4, 3), (3, 4), (4, 4)], theme.ACCENT_LIGHT)
    pack.png(f"{base}/enchanted_hit.png", ench)

    # damage indicator heart, shrunk to roughly 5x4 px
    heart = Sprite(8, 8)
    heart.points([(2, 2), (3, 2), (5, 2), (6, 2)], "#7a1022")
    heart.points([(2, 3), (3, 3), (4, 3), (5, 3), (6, 3)], "#c3203a")
    heart.points([(3, 4), (4, 4), (5, 4)], "#c3203a")
    heart.points([(4, 5)], "#7a1022")
    heart.set(3, 3, "#ff6f84")
    pack.png(f"{base}/damage.png", heart)




# =============================================================================
# Enchantment glint: a restrained cyan shimmer (vanilla is a loud purple)
# =============================================================================
def glint(pack) -> None:
    from .. import noise

    def build(seed: int, peak: tuple[int, int, int], gain: float) -> Sprite:
        n = noise.fractal(128, [(8, 0.5), (16, 0.32), (32, 0.18)], seed=seed)
        s = Sprite(128, 128)
        for y in range(128):
            for x in range(128):
                # diagonal streaking: bias the field along x+y so bands read as a sweeping shimmer
                v = n[y][x]
                a = max(0.0, min(1.0, (v - 0.46) / 0.40)) ** 1.6 * gain
                white = max(0.0, (a - 0.78) / 0.22) * 0.55
                col = tuple(min(255, round(peak[i] * a + 255 * white)) for i in range(3))
                s.set(x, y, col + (255,))
        return s

    pack.png("assets/minecraft/textures/misc/enchanted_glint_item.png", build(11, (96, 226, 255), 1.0))
    pack.json("assets/minecraft/textures/misc/enchanted_glint_item.png.mcmeta", {"texture": {"blur": True}})
    pack.png("assets/minecraft/textures/misc/enchanted_glint_armor.png", build(23, (70, 180, 235), 0.62))
    pack.json("assets/minecraft/textures/misc/enchanted_glint_armor.png.mcmeta", {"texture": {"blur": True}})


def generate(pack) -> None:
    low_fire(pack)
    overlays(pack)
    clear_water(pack)
    weather(pack)
    particles(pack)
    glint(pack)
