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
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

from sushantlite import config, theme, uv  # noqa: E402
from sushantlite.gen import armor, effects, entities, items, wings  # noqa: E402
from sushantlite.out import PackWriter  # noqa: E402
from sushantlite.sprite import Sprite, rgba  # noqa: E402
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

    def test_exactly_the_profile_materials_have_files(self):
        for material in ARMOR_ORDER:
            name = armor.FILE_NAMES[material]
            for layer in ("humanoid", "humanoid_leggings"):
                rel = f"assets/minecraft/textures/entity/equipment/{layer}/{name}.png"
                self.assertEqual((PACK / rel).exists(), config.included(rel), rel)


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
        for name, rect in entities.GLASS.items():            # the glass keeps a clear middle: the frame is under 60 %
            x, y, w, h = rect
            self.assertLess(len(opaque(img.crop((x, y, x + w, y + h)))), w * h * 0.6, name)

    def test_crystal_base_is_plain_grey(self):
        """The slab under a crystal carries no accent colour (the screenshots never show it, so vanilla's grey is the model)."""
        img = entities.crystal_texture().to_image().convert("RGBA")
        for name, (x, y, w, h) in entities.BASE.items():
            face = img.crop((x, y, x + w, y + h))
            for px, py in opaque(face):
                r, g, b, _ = face.getpixel((px, py))
                self.assertLessEqual(max(r, g, b) - min(r, g, b), 8, (name, px, py))


class CutoutAlphaTests(unittest.TestCase):
    """Cutout render types discard alpha below a threshold instead of blending: avoid half-transparent pixels."""

    def test_binary_alpha(self):
        paths = list((TEX / "entity").rglob("*.png")) + list(PACK.glob("overlay_*/assets/minecraft/textures/entity/**/*.png"))
        paths += [TEX / "block/cobweb.png"]
        self.assertGreaterEqual(len(paths), 6)               # 4 worn armor layers, the end crystal and the cobweb
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


class ScopeTests(unittest.TestCase):
    """0.4.0 is a barebones overlay: it ships only what the reference changes and leaves the rest vanilla."""

    @unittest.skipIf(config.PROFILE != "barebones", "only the barebones profile has a fixed file list")
    def test_pack_ships_exactly_the_barebones_files(self):
        actual = {p.relative_to(PACK).as_posix() for p in PACK.rglob("*") if p.is_file()}
        self.assertEqual(actual, set(config.BAREBONES))

    @unittest.skipIf(config.PROFILE != "barebones", "only the barebones profile leaves these areas to vanilla")
    def test_vanilla_areas_are_left_alone(self):
        for rel in ("assets/minecraft/textures/gui", "assets/minecraft/models", "assets/minecraft/sounds.json",
                    "assets/minecraft/particles", "assets/minecraft/textures/entity/shield", "assets/minecraft/textures/block/water_still.png"):
            self.assertFalse((PACK / rel).exists(), rel)
        self.assertEqual(list(PACK.glob("overlay_*")), [], "no per-version overlay should be needed")

    def test_included_follows_the_profile(self):
        hud = "assets/minecraft/textures/gui/sprites/hud/hotbar.png"
        with mock.patch.object(config, "PROFILE", "barebones"):
            self.assertTrue(config.included("pack.mcmeta"))
            self.assertTrue(config.included("assets/minecraft/textures/item/diamond_sword.png"))
            self.assertFalse(config.included(hud))
        with mock.patch.object(config, "PROFILE", "full"):
            self.assertTrue(config.included(hud))

    def test_writer_skips_files_outside_the_profile(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(config, "PROFILE", "barebones"):
            w = PackWriter(Path(tmp))
            w.png("assets/minecraft/textures/gui/sprites/hud/hotbar.png", Sprite(4, 4))
            w.png("assets/minecraft/textures/item/bow.png", Sprite(16, 16))
            self.assertEqual(w.written, {"assets/minecraft/textures/item/bow.png"})
            self.assertFalse((Path(tmp) / "assets/minecraft/textures/gui").exists())


class LookTests(unittest.TestCase):
    """The look measured on the reference: blue diamond, dusty-violet netherite, orange gold, no gem decoration."""

    def test_diamond_sword_has_light_flanks_round_a_mid_centre(self):
        head = theme.TOOL_HEADS["diamond"]
        img = Image.open(TEX / "item/diamond_sword.png").convert("RGBA")
        self.assertEqual(img.getpixel((8, 8))[:3], rgb(head.m))     # centre line (x + y == 16)
        self.assertEqual(img.getpixel((8, 7))[:3], rgb(head.l))     # upper flank (x + y == 15, not one of the glint cells)
        self.assertEqual(img.getpixel((14, 1))[:3], rgb(head.s))    # tip glint

    def test_sword_blade_is_three_pixels_wide(self):
        for y in range(4, 10):
            self.assertEqual(items.SWORD[y].count("B"), 3, f"row {y}")

    def test_blade_colours_are_blue_violet_and_orange(self):
        d, n, g = (rgb(theme.TOOL_HEADS[m].m) for m in ("diamond", "netherite", "golden"))
        self.assertTrue(d[2] > d[1] > d[0], "diamond blue")
        self.assertTrue(n[2] > n[0] > n[1], "netherite violet")
        self.assertTrue(g[0] > g[1] > g[2], "gold orange")
        for kind in ("sword",):
            self.assertIn(d, colours(TEX / f"item/diamond_{kind}.png"))
            self.assertIn(n, colours(TEX / f"item/netherite_{kind}.png"))
            self.assertIn(g, colours(TEX / f"item/golden_{kind}.png"))

    def test_diamond_tool_heads_are_bright_cyan(self):
        fill = rgb(theme.TOOL_FILL["diamond"].m)
        for kind in ("pickaxe", "axe", "shovel", "hoe"):
            self.assertIn(fill, colours(TEX / f"item/diamond_{kind}.png"), kind)

    def test_diamond_and_netherite_outlines_are_coloured_not_black(self):
        out = Image.open(TEX / "item/diamond_sword.png").convert("RGBA").getpixel((15, 0))     # outside the tip
        self.assertTrue(out[3] == 255 and out[2] > out[1] > out[0], out)
        out = Image.open(TEX / "item/netherite_sword.png").convert("RGBA").getpixel((15, 0))
        self.assertTrue(out[3] == 255 and out[2] > out[0] > out[1], out)

    def test_no_cyan_gem_decoration(self):
        gem = {rgb(theme.ACCENT), rgb(theme.ACCENT_DARK), rgb(theme.ACCENT_LIGHT)}
        paths = [TEX / f"item/{m}_sword.png" for m in config.SWORD_MATERIALS]
        paths += [TEX / f"item/diamond_{k}.png" for k in ("pickaxe", "axe", "shovel", "hoe")]
        paths += [TEX / f"item/{m}_{p}.png" for m in ("diamond", "netherite") for p in ("helmet", "chestplate", "leggings", "boots")]
        paths += [TEX / f"item/{n}.png" for n in ("totem_of_undying", "bow", "ender_pearl")]
        paths += list((TEX / "entity/equipment").glob("humanoid*/*.png"))
        self.assertGreaterEqual(len(paths), 25)
        for path in paths:
            self.assertFalse(gem & colours(path), f"{path.relative_to(PACK)} still carries an accent-coloured gem pixel")

    def test_totem_has_a_green_outline_and_green_eyes(self):
        img = Image.open(TEX / "item/totem_of_undying.png").convert("RGBA")
        r, g, b, a = img.getpixel((6, 3))                    # an eye
        self.assertTrue(a == 255 and g > r + 60 and g > b + 60, (r, g, b))
        r, g, b, a = img.getpixel((5, 0))                    # the outline above the head
        self.assertTrue(a == 255 and g > r and g > b, (r, g, b))

    def test_cobweb_is_an_open_cyan_web_in_a_cyan_frame(self):
        img = Image.open(TEX / "block/cobweb.png").convert("RGBA")
        pts = opaque(img)
        self.assertTrue(0.50 <= len(pts) / 256 <= 0.68, f"{len(pts) / 256:.0%} opaque")   # chunky: about half of it is open
        for (x, y) in pts:
            r, g, b, a = img.getpixel((x, y))
            self.assertTrue(g > r + 60 and b > r + 60, ((x, y), (r, g, b)))
        for xy in ((0, 5), (15, 9), (6, 0), (9, 15), (0, 0), (15, 15)):
            self.assertEqual(img.getpixel(xy)[3], 255, xy)           # the frame is closed

    def test_end_crystal_frame_is_pale_steel_and_core_is_pink_violet(self):
        img = Image.open(TEX / "entity/end_crystal/end_crystal.png").convert("RGBA")
        gx, gy, _gw, _gh = entities.GLASS["front"]
        r, g, b, a = img.getpixel((gx, gy + 8))             # middle of the left frame edge
        self.assertTrue(a == 255 and min(r, g, b) > 120 and b >= g >= r and b - r < 60, (r, g, b, a))
        cx, cy, cw, ch = entities.CORE["front"]
        r, g, b, a = img.getpixel((cx + cw // 2, cy + ch // 2))
        self.assertTrue(a == 255 and r > g and b > g, (r, g, b, a))

    def test_fire_is_low_amber_and_in_both_variants(self):
        for name in ("fire_0", "fire_1"):
            strip = Image.open(TEX / f"block/{name}.png").convert("RGBA")
            self.assertEqual(strip.size, (16, 512), name)
            self.assertTrue((TEX / f"block/{name}.png.mcmeta").exists(), name)
            for f in range(32):
                frame = strip.crop((0, f * 16, 16, f * 16 + 16))
                top = min((y for y in range(16) for x in range(16) if frame.getpixel((x, y))[3] > 0), default=16)
                self.assertGreaterEqual(top, 5, f"{name} frame {f}: flame reaches row {top}")
        for r, g, b in colours(TEX / "block/fire_1.png"):
            self.assertTrue(r >= 160 and r > g > b and b <= 210, (r, g, b))      # amber / orange / pale yellow, never red or blue


class ToolingTests(unittest.TestCase):
    def test_partial_run_keeps_overlay_entries(self):
        """Regression: ``generate.py --only armor`` used to drop the overlays from pack.mcmeta.

        The barebones pack has no overlay files, so the previous manifest is simulated: it lists one file in
        each overlay, as the full profile's manifest does."""
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "generated-files.txt"
            manifest.write_text("\n".join(f"{name}/assets/minecraft/x.png" for name in config.OVERLAYS) + "\n")
            with mock.patch.object(config, "GENERATED_MANIFEST", manifest):
                full = PackWriter(Path(tmp) / "pack")
                partial = PackWriter(Path(tmp) / "pack", partial=True)
                self.assertEqual(full.used_overlays(), set())
                self.assertEqual(partial.used_overlays(), set(config.OVERLAYS))


if __name__ == "__main__":
    unittest.main()
