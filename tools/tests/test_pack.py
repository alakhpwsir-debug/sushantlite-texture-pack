"""Regression tests for the generators' invariants.   Run:  python -m unittest discover -s tools/tests -v

They need only Pillow and the committed pack (no Minecraft files).  The structural checks against the
vanilla asset lists live in ``tools/validate.py``; these tests cover what the validator cannot know:
the UV rules behind the entity textures, tint behaviour and the generator tooling itself.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

from sushantlite import config, theme, uv  # noqa: E402
from sushantlite.gen import armor, entities, items, models, wings  # noqa: E402
from sushantlite.out import PackWriter  # noqa: E402
from sushantlite.sprite import rgba  # noqa: E402
from sushantlite.theme import ARMOR_ORDER, MATERIAL_ORDER  # noqa: E402

PACK = config.PACK_DIR
TEX = PACK / "assets/minecraft/textures"


def opaque(img: Image.Image) -> set:
    img = img.convert("RGBA")
    return {(x, y) for y in range(img.height) for x in range(img.width) if img.getpixel((x, y))[3] > 0}


class UvTests(unittest.TestCase):
    def test_box_unwrap_matches_the_standard_cross(self):
        f = uv.box_faces(0, 0, 8, 8, 8)                      # the humanoid head
        self.assertEqual(f["front"], (8, 8, 8, 8))
        self.assertEqual(f["top"], (8, 0, 8, 8))
        self.assertEqual(f["west"], (0, 8, 8, 8))
        self.assertEqual(f["back"], (24, 8, 8, 8))
        body = uv.box_faces(16, 16, 8, 12, 4)
        self.assertEqual(body["front"], (20, 20, 8, 12))
        self.assertEqual(body["back"], (32, 20, 8, 12))

    def test_scale_doubles_every_number(self):
        one, two = uv.box_faces(32, 0, 8, 8, 8), uv.box_faces(32, 0, 8, 8, 8, scale=2)
        for name in one:
            self.assertEqual(two[name], tuple(c * 2 for c in one[name]))


class ArmorTests(unittest.TestCase):
    def test_layer_sizes_and_disjoint_pieces(self):
        for regions, expected in ((armor.layer1_regions(), 648), (armor.layer2_regions(), 280)):   # = vanilla iron / copper / gold
            total = sum(len(r.cells) for r in regions)
            self.assertEqual(total, expected)
            self.assertEqual(len(armor.coverage(regions)), expected, "two pieces paint the same pixel")

    def test_textures_paint_exactly_the_covered_cells(self):
        l1, l2 = armor.coverage(armor.layer1_regions()), armor.coverage(armor.layer2_regions())
        for material, (outer, inner) in armor.textures().items():
            self.assertEqual(opaque(outer.to_image()), l1, material)
            self.assertEqual(opaque(inner.to_image()), l2, material)

    def test_all_materials_have_files(self):
        for material in ARMOR_ORDER:
            name = armor.FILE_NAMES[material]
            for layer in ("humanoid", "humanoid_leggings"):
                self.assertTrue((TEX / f"entity/equipment/{layer}/{name}.png").exists(), (layer, name))


class EntityTests(unittest.TestCase):
    def test_sizes(self):
        self.assertEqual(entities.arrow_texture(entities.ARROW).to_image().size, (32, 32))
        self.assertEqual(entities.trident_texture().to_image().size, (32, 32))
        self.assertEqual(entities.xp_orb_texture().to_image().size, (64, 64))
        self.assertEqual(entities.bobber_texture().to_image().size, (8, 8))
        self.assertEqual(entities.crystal_texture().to_image().size, (128, 64))
        self.assertEqual(wings.wing_texture().to_image().size, (64, 32))

    def test_tipped_arrow_is_tint_neutral(self):
        """The potion colour is multiplied over this texture, so it must be grey/white only."""
        img = entities.arrow_texture(entities.TIPPED).to_image().convert("RGBA")
        for (x, y) in opaque(img):
            r, g, b, _ = img.getpixel((x, y))
            self.assertLessEqual(max(r, g, b) - min(r, g, b), 6, (x, y))

    def test_arrow_halves_mirror(self):
        img = entities.arrow_texture(entities.ARROW).to_image().convert("RGBA")
        for y in range(5):
            for x in range(16):
                self.assertEqual(img.getpixel((x, y)), img.getpixel((31 - x, y)), (x, y))

    def test_orb_sprites_stay_inside_their_cell_and_grow(self):
        img = entities.xp_orb_texture().to_image().convert("RGBA")
        counts = []
        for i in range(11):
            cx, cy = (i % 4) * 16, (i // 4) * 16
            cell = img.crop((cx, cy, cx + 16, cy + 16))
            pts = opaque(cell)
            self.assertTrue(pts, f"orb cell {i} is empty")
            counts.append(len(pts))
        self.assertEqual(counts, sorted(counts), "orbs must not shrink as the value bracket grows")

    def test_crystal_regions(self):
        img = entities.crystal_texture().to_image().convert("RGBA")
        for name, rect in entities.CORE.items():             # the core is solid
            x, y, w, h = rect
            self.assertEqual(len(opaque(img.crop((x, y, x + w, y + h)))), w * h, name)
        for name, rect in entities.GLASS.items():            # the glass is mostly clear
            x, y, w, h = rect
            self.assertLess(len(opaque(img.crop((x, y, x + w, y + h)))), w * h * 0.4, name)


class CutoutAlphaTests(unittest.TestCase):
    """Cutout render types discard alpha below a threshold instead of blending: avoid half-transparent pixels."""

    def test_binary_alpha(self):
        paths = list((TEX / "entity").rglob("*.png")) + list(PACK.glob("overlay_*/assets/minecraft/textures/entity/**/*.png"))
        paths += [TEX / "block/cobweb.png"]
        self.assertGreater(len(paths), 20)
        for path in paths:
            if path.name in ("experience_orb.png",):         # translucent render type
                continue
            img = Image.open(path).convert("RGBA")
            alphas = {img.getpixel((x, y))[3] for y in range(img.height) for x in range(img.width)}
            self.assertTrue(alphas <= {0, 255}, f"{path.relative_to(PACK)} has partial alpha {sorted(alphas)}")


def rgb(colour) -> tuple:
    return rgba(colour)[:3]


def colours(path) -> set:
    img = Image.open(path).convert("RGBA")
    return {img.getpixel(p)[:3] for p in opaque(img)}


class LookTests(unittest.TestCase):
    """The 0.3.0 look: neutral HUD, blue diamond / violet netherite tools, no gem decoration, bold details."""

    def test_hotbar_is_neutral_grey(self):
        for name in ("hotbar", "hotbar_offhand_left", "hotbar_offhand_right"):
            for r, g, b in colours(TEX / f"gui/sprites/hud/{name}.png"):
                self.assertLessEqual(max(r, g, b) - min(r, g, b), 14, (name, (r, g, b)))

    def test_selection_ring_is_white_outside(self):
        img = Image.open(TEX / "gui/sprites/hud/hotbar_selection.png").convert("RGBA")
        r, g, b, a = img.getpixel((1, 11))                  # left side, second ring column
        self.assertEqual(a, 255)
        self.assertGreaterEqual(min(r, g, b), 230)

    def test_diamond_tools_are_blue_and_netherite_violet(self):
        dr, dg, db = rgb(theme.TOOL_HEADS["diamond"].m)
        nr, ng, nb = rgb(theme.TOOL_HEADS["netherite"].m)
        self.assertTrue(db > dg > dr, "diamond tool body must be blue")
        self.assertTrue(nb > nr > ng, "netherite tool body must be violet")
        for kind in ("sword", "axe", "pickaxe", "shovel", "hoe", "spear"):
            self.assertIn((dr, dg, db), colours(TEX / f"item/diamond_{kind}.png"), kind)
            self.assertIn((nr, ng, nb), colours(TEX / f"item/netherite_{kind}.png"), kind)

    def test_no_cyan_gem_decoration(self):
        gem = {rgb(theme.ACCENT), rgb(theme.ACCENT_DARK), rgb(theme.ACCENT_LIGHT)}
        paths = [TEX / f"item/{m}_{k}.png" for m in MATERIAL_ORDER for k in ("sword", "axe", "pickaxe", "shovel", "hoe", "spear")]
        paths += [TEX / f"item/{m}_{p}.png" for m in ARMOR_ORDER for p in ("helmet", "chestplate", "leggings", "boots")]
        paths += [TEX / f"item/{n}.png" for n in ("totem_of_undying", "mace", "bow", "arrow")]
        paths += list((TEX / "entity/equipment").glob("humanoid*/*.png"))
        self.assertGreater(len(paths), 60)
        for path in paths:
            self.assertFalse(gem & colours(path), f"{path.relative_to(PACK)} still carries an accent-coloured gem pixel")

    def test_sword_blade_is_three_pixels_wide(self):
        for y in range(4, 10):
            self.assertEqual(items.SWORD[y].count("B"), 3, f"row {y}")

    def test_cobweb_has_a_cyan_frame(self):
        img = Image.open(TEX / "block/cobweb.png").convert("RGBA")
        for xy in ((0, 5), (15, 9), (6, 0), (9, 15), (0, 0), (15, 15)):
            r, g, b, a = img.getpixel(xy)
            self.assertEqual(a, 255, xy)
            self.assertTrue(b > r and g > r, xy)

    def test_end_crystal_frame_is_cyan_and_core_is_magenta(self):
        img = Image.open(TEX / "entity/end_crystal/end_crystal.png").convert("RGBA")
        gx, gy, _gw, _gh = entities.GLASS["front"]
        r, g, b, a = img.getpixel((gx, gy + 8))             # middle of the left frame edge
        self.assertTrue(a == 255 and b > r and g > r, (r, g, b, a))
        cx, cy, cw, ch = entities.CORE["front"]
        r, g, b, a = img.getpixel((cx + cw // 2, cy + ch // 2))
        self.assertTrue(a == 255 and r > g and b > g, (r, g, b, a))

    def test_fire_is_low_in_both_variants(self):
        for name in ("fire_0", "fire_1"):
            strip = Image.open(TEX / f"block/{name}.png").convert("RGBA")
            self.assertEqual(strip.size, (16, 512), name)
            self.assertTrue((TEX / f"block/{name}.png.mcmeta").exists(), name)
            for f in range(32):
                frame = strip.crop((0, f * 16, 16, f * 16 + 16))
                top = min((y for y in range(16) for x in range(16) if frame.getpixel((x, y))[3] > 0), default=16)
                self.assertGreaterEqual(top, 5, f"{name} frame {f}: flame reaches row {top}")

    def test_only_changed_models_ship(self):
        shipped = {
            "handheld": ["handheld"], "generated": ["generated"], "bow": ["bow", "crossbow"],
            "mace": ["handheld_mace"], "spear": ["spear_in_hand"],
        }
        for key, files in shipped.items():
            for name in files:
                exists = (PACK / f"assets/minecraft/models/item/{name}.json").exists()
                self.assertEqual(exists, models.changed(key), f"{name} (SCALES[{key!r}])")
        self.assertTrue(models.changed("shield"))
        self.assertTrue(models.changed("totem_pop"))
        for name in ("shield", "shield_blocking", "totem_of_undying"):
            self.assertTrue((PACK / f"assets/minecraft/models/item/{name}.json").exists(), name)


class ToolingTests(unittest.TestCase):
    def test_partial_run_keeps_overlay_entries(self):
        """Regression: ``generate.py --only armor`` used to drop the overlays from pack.mcmeta."""
        with tempfile.TemporaryDirectory() as tmp:
            full = PackWriter(Path(tmp))
            partial = PackWriter(Path(tmp), partial=True)
            self.assertEqual(full.used_overlays(), set())
            self.assertEqual(partial.used_overlays(), set(config.OVERLAYS))


if __name__ == "__main__":
    unittest.main()
