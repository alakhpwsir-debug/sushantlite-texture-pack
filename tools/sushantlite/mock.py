"""Mock renderers used for previews and design checks (no Minecraft needed).

These are approximations meant to answer "does this look right on screen?" --
they are not a substitute for loading the pack in the game.
"""
from __future__ import annotations

import math
from typing import Callable, Sequence

from PIL import Image, ImageDraw, ImageFont


# --------------------------------------------------------------------------- fonts
def font(size: int = 11):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


# --------------------------------------------------------------------------- backdrops
def sky_backdrop(w: int, h: int) -> Image.Image:
    """A flat, game-ish scene: sky gradient, grass ground, a couple of blocks."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    horizon = int(h * 0.58)
    for y in range(h):
        for x in range(w):
            if y < horizon:
                t = y / horizon
                px[x, y] = (int(112 + 40 * t), int(172 + 36 * t), int(238 - 10 * t), 255)
            else:
                t = (y - horizon) / max(1, h - horizon)
                shade = 1.0 - 0.28 * t
                checker = ((x // 24) + (y // 12)) % 2
                base = (92, 150, 62) if checker else (86, 140, 58)
                px[x, y] = tuple(int(c * shade) for c in base) + (255,)
    d = ImageDraw.Draw(img)
    d.rectangle([w * 0.62, horizon - h * 0.16, w * 0.62 + w * 0.11, horizon + h * 0.04], fill=(122, 92, 58, 255))
    d.rectangle([w * 0.62, horizon - h * 0.16, w * 0.62 + w * 0.11, horizon - h * 0.13], fill=(96, 164, 70, 255))
    return img


def checker(w: int, h: int, cell: int = 8, a=(52, 56, 66), b=(44, 48, 58)) -> Image.Image:
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (a if ((x // cell) + (y // cell)) % 2 == 0 else b) + (255,)
    return img


# --------------------------------------------------------------------------- fire overlay
def fire_screen(strip: Image.Image, frame: int, fov: float = 70.0, size: tuple[int, int] = (384, 216),
                backdrop: Image.Image | None = None) -> Image.Image:
    """Approximate the first-person fire overlay for an animation strip of 16x16 frames.

    Geometry (from the vanilla render code): two 1x1 quads at depth 0.5, centred at x = +-0.24 and
    shifted down by 0.3, each sampling the middle 75 % of the frame; colour alpha 0.9.
    (The +-10 degree yaw of the quads is ignored.)
    """
    w, h = size
    out = (backdrop or sky_backdrop(w, h)).copy().convert("RGBA")
    px = out.load()
    fr = strip.crop((0, frame * 16, 16, frame * 16 + 16)).convert("RGBA").load()
    half_h = 0.5 * math.tan(math.radians(fov) / 2)
    half_w = half_h * (w / h)
    for sy in range(h):
        Y = half_h * (1 - 2 * (sy + 0.5) / h)
        t = (0.2 - Y) / 1.0
        if not 0 <= t <= 1:
            continue
        row = min(15, int((0.125 + 0.75 * t) * 16))
        for sx in range(w):
            X = half_w * (2 * (sx + 0.5) / w - 1)
            for cx in (0.24, -0.24):
                u = X - (cx - 0.5)
                if not 0 <= u <= 1:
                    continue
                col = min(15, int((0.125 + 0.75 * u) * 16))
                r, g, b, a = fr[col, row]
                if a:
                    k = a / 255 * 0.9
                    br, bg, bb, _ = px[sx, sy]
                    px[sx, sy] = (round(br + (r - br) * k), round(bg + (g - bg) * k), round(bb + (b - bb) * k), 255)
    return out


# --------------------------------------------------------------------------- sheets
def labelled_grid(cells: Sequence[tuple[str, Image.Image]], cols: int, cell: int = 16, scale: int = 6,
                  pad: int = 6, label_h: int = 14, bg=(30, 33, 42), show_labels: bool = True,
                  tile_bg: bool = True) -> Image.Image:
    """Lay out sprites on a grid at ``scale``x with an optional caption under each."""
    f = font(9)
    cw = cell * scale + pad * 2
    ch = cell * scale + pad * 2 + (label_h if show_labels else 0)
    rows = math.ceil(len(cells) / cols)
    sheet = Image.new("RGBA", (cols * cw, rows * ch), bg + (255,))
    d = ImageDraw.Draw(sheet)
    for i, (label, img) in enumerate(cells):
        cx, cy = (i % cols) * cw, (i // cols) * ch
        tile = checker(cell * scale, cell * scale, cell=scale * 2) if tile_bg else Image.new("RGBA", (cell * scale,) * 2, bg + (255,))
        im = img.convert("RGBA")
        k = max(1, min(scale, (cell * scale) // max(im.width, im.height)))
        im = im.resize((im.width * k, im.height * k), Image.NEAREST)
        tile.alpha_composite(im, ((cell * scale - im.width) // 2, (cell * scale - im.height) // 2))
        sheet.alpha_composite(tile, (cx + pad, cy + pad))
        if show_labels:
            d.text((cx + pad, cy + pad + cell * scale + 2), label[: cw // 5], fill=(190, 200, 215, 255), font=f)
    return sheet


# --------------------------------------------------------------------------- HUD
def hud_screen(pack_dir, items: dict[int, Image.Image] | None = None, offhand_item: Image.Image | None = None,
               scale: int = 3, gui_w: int = 320, gui_h: int = 180, selected: int = 2,
               full_hearts: float = 7.5, hunger: float = 8.5, armor: int = 17, air_bubbles: int = 6,
               xp: float = 0.62, backdrop: Image.Image | None = None) -> Image.Image:
    """Compose a survival HUD from the pack's own sprites using the vanilla layout (GUI scale 1 coords)."""
    from pathlib import Path
    sp = Path(pack_dir) / "assets/minecraft/textures/gui/sprites/hud"

    def load(name: str) -> Image.Image:
        return Image.open(sp / name).convert("RGBA")

    canvas = (backdrop or sky_backdrop(gui_w * scale, gui_h * scale)).copy().convert("RGBA")
    canvas = canvas.resize((gui_w, gui_h), Image.LANCZOS)          # draw everything at GUI scale 1, enlarge at the end
    cx = gui_w // 2

    def put(img, x, y):
        canvas.alpha_composite(img, (int(x), int(y)))

    hx, hy = cx - 91, gui_h - 22
    put(load("hotbar_offhand_left.png"), hx - 29, hy - 1)
    put(load("hotbar.png"), hx, hy)
    put(load("hotbar_selection.png"), hx - 1 + 20 * selected, hy - 1)
    for slot, icon in (items or {}).items():
        put(icon, hx + 3 + 20 * slot, hy + 3)
    if offhand_item is not None:
        put(offhand_item, hx - 29 + 3, hy - 1 + 4)

    # experience bar
    put(load("experience_bar_background.png"), hx, gui_h - 29)
    fill = load("experience_bar_progress.png").crop((0, 0, int(182 * xp), 5))
    put(fill, hx, gui_h - 29)

    # hearts (left), food (right), armour, air
    y_h = gui_h - 39
    for i in range(10):
        put(load("heart/container.png"), hx + i * 8, y_h)
        if i + 1 <= int(full_hearts):
            put(load("heart/full.png"), hx + i * 8, y_h)
        elif i < full_hearts:
            put(load("heart/half.png"), hx + i * 8, y_h)
    for i in range(10):
        x = hx + 182 - 9 - i * 8
        put(load("food_empty.png"), x, y_h)
        if i + 1 <= int(hunger):
            put(load("food_full.png"), x, y_h)
        elif i < hunger:
            put(load("food_half.png"), x, y_h)
    for i in range(10):
        state = "full" if (i + 1) * 2 <= armor else "half" if i * 2 < armor else "empty"
        put(load(f"armor_{state}.png"), hx + i * 8, y_h - 10)
    for i in range(10):
        put(load("air.png" if i < air_bubbles else "air_empty.png"), hx + 182 - 9 - i * 8, y_h - 10)

    # crosshair: inverting blend, like the game
    ch = load("crosshair.png")
    ox, oy = cx - 7, gui_h // 2 - 7
    px = canvas.load()
    for y in range(ch.height):
        for x in range(ch.width):
            if ch.getpixel((x, y))[3]:
                r, g, b, _ = px[ox + x, oy + y]
                px[ox + x, oy + y] = (255 - r, 255 - g, 255 - b, 255)

    return canvas.resize((gui_w * scale, gui_h * scale), Image.NEAREST)
