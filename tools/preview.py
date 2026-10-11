#!/usr/bin/env python3
"""Render preview sheets (docs/previews/*.png) from the pack's own textures.

    python tools/preview.py

The sheets are mock-ups (HUD layout, fire overlay projection, additive sky blending)
made only from SushantLite's files -- no Mojang art is involved.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageDraw  # noqa: E402

from sushantlite import config, mock  # noqa: E402
from sushantlite.theme import ARMOR_ORDER, MATERIAL_ORDER  # noqa: E402

OUT = config.DOCS_DIR / "previews"
TEX = config.PACK_DIR / "assets/minecraft/textures"


def img(rel: str) -> Image.Image:
    return Image.open(TEX / rel).convert("RGBA")


def tinted_potion(kind: str, rgb) -> Image.Image:
    overlay = img("item/potion_overlay.png")
    px = overlay.load()
    for y in range(overlay.height):
        for x in range(overlay.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r * rgb[0] // 255, g * rgb[1] // 255, b * rgb[2] // 255, a)
    overlay.alpha_composite(img(f"item/{kind}.png"))
    return overlay


# --------------------------------------------------------------------------- sheets
def hud_sheet() -> Image.Image:
    items = {
        0: img("item/diamond_sword.png"),
        1: img("item/diamond_axe.png"),
        2: img("item/bow.png"),
        3: img("item/ender_pearl.png"),
        4: img("item/golden_apple.png"),
        5: tinted_potion("splash_potion", (248, 36, 35)),
        6: tinted_potion("potion", (124, 175, 198)),
        7: img("item/end_crystal.png"),
        8: img("item/netherite_pickaxe.png"),
    }
    return mock.hud_screen(config.PACK_DIR, items=items, offhand_item=img("item/totem_of_undying.png"),
                           selected=0, scale=3, gui_w=320, gui_h=180).convert("RGB")


def items_sheet() -> Image.Image:
    cells = []
    for kind in ("sword", "axe", "pickaxe", "shovel", "hoe", "spear"):
        for m in MATERIAL_ORDER:
            cells.append((f"{m} {kind}", img(f"item/{m}_{kind}.png")))
    tools = mock.labelled_grid(cells, cols=7, cell=16, scale=6, pad=3, label_h=0, show_labels=False)
    armor = [(f"{m} {p}", img(f"item/{m}_{p}.png")) for p in ("helmet", "chestplate", "leggings", "boots") for m in ARMOR_ORDER]
    armor_sheet = mock.labelled_grid(armor, cols=6, cell=16, scale=6, pad=3, label_h=0, show_labels=False)
    misc_names = ["mace", "bow", "bow_pulling_2", "arrow", "totem_of_undying", "golden_apple", "enchanted_golden_apple",
                  "ender_pearl", "end_crystal", "experience_bottle"]
    misc = [(n, img(f"item/{n}.png")) for n in misc_names]
    misc += [("healing", tinted_potion("potion", (248, 36, 35))), ("splash", tinted_potion("splash_potion", (124, 175, 198))),
             ("lingering", tinted_potion("lingering_potion", (147, 36, 35)))]
    misc_sheet = mock.labelled_grid(misc, cols=7, cell=16, scale=6, pad=3, label_h=0, show_labels=False)
    w = max(tools.width, armor_sheet.width, misc_sheet.width)
    h = tools.height + armor_sheet.height + misc_sheet.height + 20
    sheet = Image.new("RGBA", (w, h), (30, 33, 42, 255))
    y = 0
    for part in (tools, armor_sheet, misc_sheet):
        sheet.alpha_composite(part, (0, y))
        y += part.height + 10
    return sheet.convert("RGB")


def shield_sheet() -> Image.Image:
    """Front of the plain shield, banner-tinted examples of the tintable base, and the inside."""
    root = config.PACK_DIR / "overlay_26_1/assets/minecraft/textures/entity/shield"
    plain = Image.open(root / "shield_base_nopattern.png").convert("RGBA")
    base = Image.open(root / "shield_base.png").convert("RGBA")
    S = 9

    def face(src, box):
        return src.crop((box[0], box[1], box[0] + 12, box[1] + 22))

    def tint(im, rgb):
        out = im.copy()
        px = out.load()
        for yy in range(out.height):
            for xx in range(out.width):
                r, g, b, a = px[xx, yy]
                px[xx, yy] = (r * rgb[0] // 255, g * rgb[1] // 255, b * rgb[2] // 255, a)
        return out

    tiles = [("plain (front)", face(plain, (1, 1))), ("plain (inside)", face(plain, (14, 1)))]
    for name, rgb in (("red banner", (176, 46, 38)), ("blue banner", (60, 68, 170)), ("white banner", (255, 255, 255))):
        tiles.append((name, tint(face(base, (1, 1)), rgb)))
    f = mock.font(11)
    sheet = Image.new("RGBA", (len(tiles) * (12 * S + 24) + 12, 22 * S + 52), (30, 33, 42, 255))
    d = ImageDraw.Draw(sheet)
    for i, (label, tile) in enumerate(tiles):
        x = 12 + i * (12 * S + 24)
        bg = mock.checker(12 * S, 22 * S, cell=S * 2)
        bg.alpha_composite(tile.resize((12 * S, 22 * S), Image.NEAREST))
        sheet.alpha_composite(bg, (x, 12))
        d.text((x, 22 * S + 20), label, fill=(200, 210, 230, 255), font=f)
    return sheet.convert("RGB")


def fire_sheet() -> Image.Image:
    strip = img("block/fire_1.png")
    W, H = 320, 180
    f = mock.font(12)
    sheet = Image.new("RGBA", (W * 3 + 40, (H + 26) * 2 + 14), (20, 22, 30, 255))
    d = ImageDraw.Draw(sheet)
    for r, frame in enumerate((4, 20)):
        for c, fov in enumerate((70, 90, 110)):
            scr = mock.fire_screen(strip, frame=frame, fov=fov, size=(W, H))
            x, y = 10 + c * (W + 10), 8 + r * (H + 26)
            d.text((x, y), f"low fire - FOV {fov} (frame {frame})", fill=(220, 230, 240, 255), font=f)
            sheet.alpha_composite(scr, (x, y + 16))
    return sheet.convert("RGB")


def sky_sheet() -> Image.Image:
    f = mock.font(11)
    sheet = Image.new("RGB", (900, 330), (16, 20, 34))
    d = ImageDraw.Draw(sheet)

    def additive(base: Image.Image, tex: Image.Image, scale: int) -> Image.Image:
        t = tex.convert("RGB").resize((tex.width * scale, tex.height * scale), Image.NEAREST)
        out = base.copy()
        px, tp = out.load(), t.load()
        for y in range(t.height):
            for x in range(t.width):
                r, g, b = px[x, y]
                tr, tg, tb = tp[x, y]
                px[x, y] = (min(255, r + tr), min(255, g + tg), min(255, b + tb))
        return out

    sun = additive(Image.new("RGB", (160, 160), (118, 170, 240)), img("environment/celestial/sun.png"), 5)
    sheet.paste(sun, (10, 24))
    d.text((10, 6), "sun", fill=(200, 210, 230), font=f)
    phases = ["new_moon", "waxing_crescent", "first_quarter", "waxing_gibbous", "full_moon", "waning_gibbous",
              "third_quarter", "waning_crescent"]
    for i, ph in enumerate(phases):
        tile = additive(Image.new("RGB", (112, 112), (10, 14, 40)), img(f"environment/celestial/moon/{ph}.png"), 3).crop((0, 0, 96, 96))
        sheet.paste(tile, (190 + (i % 4) * 104, 24 + (i // 4) * 104))
    d.text((190, 6), "moon phases", fill=(200, 210, 230), font=f)
    clouds = img("environment/clouds.png")
    bg = Image.new("RGBA", clouds.size, (86, 130, 210, 255))
    bg.alpha_composite(clouds)
    sheet.paste(bg.convert("RGB").resize((280, 280), Image.NEAREST), (620, 24))
    d.text((620, 6), "clouds", fill=(200, 210, 230), font=f)
    return sheet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("hud", hud_sheet), ("items", items_sheet), ("shield", shield_sheet), ("low-fire", fire_sheet), ("sky", sky_sheet)]:
        im = fn()
        im.save(OUT / f"{name}.png", optimize=True)
        print(f"docs/previews/{name}.png  {im.width}x{im.height}")


if __name__ == "__main__":
    main()
