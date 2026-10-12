#!/usr/bin/env python3
"""Render preview sheets (docs/previews/*.png) from the pack's own textures.

    python tools/preview.py

The sheets are mock-ups (a hotbar drawn from plain grey squares, the fire overlay projection,
flat paper dolls) made only from SushantLite's own files -- no Mojang art is involved.  Since 0.4.0
the pack no longer changes the HUD, so there is no HUD sheet: the hotbar mock-up only shows how the
pack's item icons sit in a slot.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageDraw  # noqa: E402

from sushantlite import config, mock  # noqa: E402

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
def hotbar_sheet() -> Image.Image:
    """The pack's icons in a plain grey mock hotbar (the real hotbar is vanilla's) over a grassy backdrop."""
    scale, slot = 4, 20
    items = [
        img("item/diamond_sword.png"), img("item/ender_pearl.png"), img("item/diamond_axe.png"), img("item/bow.png"),
        img("item/totem_of_undying.png"), tinted_potion("splash_potion", (248, 36, 35)), img("item/diamond_chestplate.png"),
        img("item/iron_sword.png"), img("item/golden_apple.png"),
    ]
    off = img("item/netherite_sword.png")
    W, H = 200 * scale, 60 * scale
    sheet = mock.sky_backdrop(W, H)
    d = ImageDraw.Draw(sheet)
    x0, y0 = 24 * scale, 34 * scale

    def draw_slot(x: int, y: int, item: Image.Image, selected: bool = False) -> None:
        d.rectangle([x, y, x + slot * scale - 1, y + slot * scale - 1], fill=(30, 30, 30, 235), outline=(139, 139, 139, 255), width=scale)
        if selected:
            d.rectangle([x - scale, y - scale, x + slot * scale, y + slot * scale], outline=(240, 244, 246, 255), width=scale)
        sheet.alpha_composite(item.resize((16 * scale, 16 * scale), Image.NEAREST), (x + 2 * scale, y + 2 * scale))

    draw_slot(x0 - 26 * scale, y0, off)
    for i, it in enumerate(items):
        draw_slot(x0 + i * slot * scale, y0, it, selected=(i == 0))
    d.text((6, 6), "mock-up: the hotbar itself is vanilla; only the item icons come from SushantLite", fill=(255, 255, 255, 255), font=mock.font(13))
    return sheet.convert("RGB")


def items_sheet() -> Image.Image:
    cells = [(f"{m} sword", img(f"item/{m}_sword.png")) for m in config.SWORD_MATERIALS]
    cells += [(f"diamond {k}", img(f"item/diamond_{k}.png")) for k in ("pickaxe", "axe", "shovel", "hoe")]
    top = mock.labelled_grid(cells, cols=5, cell=16, scale=6, pad=3, label_h=0, show_labels=False)
    armor = [(f"{m} {p}", img(f"item/{m}_{p}.png")) for m in ("diamond", "netherite") for p in ("helmet", "chestplate", "leggings", "boots")]
    armor_sheet_ = mock.labelled_grid(armor, cols=8, cell=16, scale=6, pad=3, label_h=0, show_labels=False)
    misc_names = ["bow", "bow_pulling_0", "bow_pulling_1", "bow_pulling_2", "ender_pearl", "golden_apple", "apple", "totem_of_undying"]
    misc = [(n, img(f"item/{n}.png")) for n in misc_names]
    misc += [("healing", tinted_potion("potion", (248, 36, 35))), ("splash", tinted_potion("splash_potion", (124, 175, 198))),
             ("lingering", tinted_potion("lingering_potion", (147, 36, 35)))]
    misc_sheet = mock.labelled_grid(misc, cols=8, cell=16, scale=6, pad=3, label_h=0, show_labels=False)
    w = max(top.width, armor_sheet_.width, misc_sheet.width)
    h = top.height + armor_sheet_.height + misc_sheet.height + 20
    sheet = Image.new("RGBA", (w, h), (30, 33, 42, 255))
    y = 0
    for part in (top, armor_sheet_, misc_sheet):
        sheet.alpha_composite(part, (0, y))
        y += part.height + 10
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


def _label(d: ImageDraw.ImageDraw, xy, text: str) -> None:
    d.text(xy, text, fill=(190, 200, 215, 255), font=mock.font(12))


def armor_sheet() -> Image.Image:
    """Paper dolls (front + back) wearing each worn-armour set; layer 1 over layer 2 over a grey mannequin."""
    scale, gap, between = 6, 14, 14
    eq = TEX / "entity/equipment"
    names = {"diamond": "diamond", "netherite": "netherite"}
    cw = 16 * scale
    sheet = Image.new("RGBA", (len(names) * (2 * cw + between + gap * 2), 32 * scale + 44), (30, 33, 42, 255))
    d = ImageDraw.Draw(sheet)
    for i, (material, file) in enumerate(names.items()):
        outer = Image.open(eq / "humanoid" / f"{file}.png").convert("RGBA")
        inner = Image.open(eq / "humanoid_leggings" / f"{file}.png").convert("RGBA")
        x0 = i * (2 * cw + between + gap * 2) + gap
        for j, view in enumerate(("front", "back")):
            doll = mock.armor_doll(outer, inner, view).resize((cw, 32 * scale), Image.NEAREST)
            sheet.alpha_composite(doll, (x0 + j * (cw + between), 10))
        _label(d, (x0 + cw + between // 2 - 18, 32 * scale + 20), material)
    return sheet.convert("RGB")


def blocks_sheet() -> Image.Image:
    """The end crystal (core, nested glass frames) and the cobweb, flattened to a front view."""
    ent = TEX / "entity"
    sheet = Image.new("RGBA", (780, 330), (30, 33, 42, 255))
    d = ImageDraw.Draw(sheet)
    _label(d, (12, 8), "end crystal (front view)")
    c = Image.open(ent / "end_crystal/end_crystal.png").convert("RGBA")
    scene = Image.new("RGBA", (36, 36), (150, 190, 250, 255))
    scene.alpha_composite(c.crop((80, 16, 96, 32)).resize((12, 12), Image.NEAREST), (12, 12))     # core
    scene.alpha_composite(c.crop((16, 16, 32, 32)).resize((14, 14), Image.NEAREST), (11, 11))     # inner glass
    scene.alpha_composite(c.crop((16, 16, 32, 32)), (10, 10))                                      # outer glass
    sheet.alpha_composite(scene.resize((36 * 8, 36 * 8), Image.NEAREST), (12, 30))
    _label(d, (360, 8), "cobweb (on a dirt-coloured backdrop)")
    web = Image.open(TEX / "block/cobweb.png").convert("RGBA")
    back = Image.new("RGBA", (16, 16), (96, 70, 44, 255))
    back.alpha_composite(web)
    sheet.alpha_composite(back.resize((16 * 18, 16 * 18), Image.NEAREST), (360, 30))
    return sheet.convert("RGB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("hotbar", hotbar_sheet), ("items", items_sheet), ("armor", armor_sheet),
                     ("crystal-and-web", blocks_sheet), ("low-fire", fire_sheet)]:
        im = fn()
        im.save(OUT / f"{name}.png", optimize=True)
        print(f"docs/previews/{name}.png  {im.width}x{im.height}")


if __name__ == "__main__":
    main()
