"""Combat-clarity effects.

* low fire                    -> textures/block/fire_0.png + fire_1.png (first-person overlay + world flames)
* no pumpkin overlay          -> textures/misc/pumpkinblur.png
* clear underwater view       -> textures/misc/underwater.png
* clear, see-through water    -> textures/block/water_{still,flow,overlay}.png
* thin rain & snow            -> textures/environment/{rain,snow}.png
* quiet particles             -> explosions, fire/explosion smoke, death puffs and sweep arcs hidden; tiny hit sparks
* cyan cobweb                 -> textures/block/cobweb.png (a cyan frame round a dense, chunky cyan web)

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
# tips down to about row 8 and lets the flame body fade out below, so only a thin strip of
# orange (about 10-30 % of the screen height, depending on the FOV) shows along the bottom edge
# (see docs/previews/low-fire.png for the projection).
FIRE_FRAMES = 32
FIRE_TIP_ROW = 8.0          # average row of the flame tips; raise it for an even lower fire

# colour ramp, tip -> deep body: amber and orange with no red (measured on the reference overlay:
# #cf7e0f / #d58d1c / #e0a92d, yellow highlights #f3d068), plus a pale hot core inside each tongue
_FIRE_RAMP = ["#f2b236", "#ec9a22", "#e2850f", "#d4720a", "#c26106", "#a95206"]
_FIRE_CORE = ["#fff4c8", "#ffe28a", "#f8c850"]

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
    """One frame of the low-fire strip.  Periodic in ``t`` (period ``FIRE_FRAMES``) so the loop is seamless."""
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
    # fire_1 is the first-person overlay (and one of the two variants a fire block picks at random);
    # fire_0 is the other variant.  Both get the same low flame, half a period out of step so that
    # neighbouring fire blocks do not flicker in unison.  Vanilla's .mcmeta is {"animation": {}}
    # (1 tick per frame); keep that speed.
    for name, phase in (("fire_1", 0), ("fire_0", FIRE_FRAMES // 2)):
        frames = [_fire_frame(t + phase) for t in range(FIRE_FRAMES)]
        pack.animated_png(f"assets/minecraft/textures/block/{name}.png", stack_frames(frames), {})


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


# =============================================================================
# Cyan cobweb
# =============================================================================
def cobweb_sprite() -> Sprite:
    """A 1-px cyan frame round a chunky cyan web: eight thick spokes, one ragged ring and a hub.

    Cobwebs are traps, so the block carries the same bright cyan everywhere (measured on the reference:
    web #1cd2ea, frame and shaded strands #14a6ba) and about 60 % of the texture is opaque, frame included.
    Binary alpha only: the cutout render type discards partial alpha.
    """
    s = Sprite(16, 16)
    web, glint, frame = "#1cd2ea", "#6fe6f6", "#14a6ba"
    for y in range(16):
        for x in range(16):
            px, py = x + 0.5 - 8, y + 0.5 - 8
            r = math.hypot(px, py)
            d_card = min(abs(px), abs(py))                                    # horizontal / vertical spokes: 2 px
            d_diag = min(abs(px - py), abs(px + py)) / math.sqrt(2)           # diagonal spokes: 1 px
            spoke = (d_card < 0.55 or d_diag < 0.55) and r > 1.0 or r <= 1.6  # the hub is solid
            ring = abs(r - 6.0) < 0.62 and (x * 7 + y * 13) % 5 not in (0, 1)  # ragged: two cells in five are missing
            if spoke or ring:
                s.set(x, y, glint if (x + y) % 5 == 0 else web)
    s.frame(0, 0, 16, 16, frame)                 # the frame goes on last so a thread never cuts it
    return s


def cobweb(pack) -> None:
    pack.png("assets/minecraft/textures/block/cobweb.png", cobweb_sprite())


def generate(pack) -> None:
    low_fire(pack)
    overlays(pack)
    clear_water(pack)
    weather(pack)
    particles(pack)
    glint(pack)
    cobweb(pack)
