# Changelog

All notable changes to SushantLite. Versions follow `tools/sushantlite/config.py` (`PACK_VERSION`);
the supported Minecraft range is listed per release. None of the releases has been played in the game yet
(by the generator's author); see [docs/TESTING.md](docs/TESTING.md).

## 0.4.0 - barebones overlay: only what a PvP overlay changes

Minecraft 1.21.11 - 26.3 (resource-pack formats 75 - 97), unchanged. 0.3.0 redrew everything the generators could
draw; set beside the PvP overlay the owner wants to match (Barebones PvP Overlay 16x, five screenshots) it differed
in every screenshot, mostly because it replaced the HUD, which that overlay leaves vanilla. 0.4.0 fixes the **scope
first** and the art second. As before, nothing from the reference pack is used: colours and coverage figures were
measured on the owner's screenshots and every texture is drawn by the code (see [docs/STYLE.md](docs/STYLE.md)).
The match is by scope, palette and style, so it is not pixel-identical.

### Changed
- **Scope: 44 files, 24 KiB on disk (was 301 files).** The default pack now ships only what the reference changes
  (`config.BAREBONES`, an explicit allow-list that `PackWriter` enforces): the six swords, the diamond pickaxe, axe,
  shovel and hoe, diamond and netherite armor (icons and worn layers), bow with its pull stages, ender pearl, golden
  apple, apple, totem, the three potion bottles and `potion_overlay`, cobweb, `fire_0` / `fire_1`, the end crystal,
  `critical_hit` and clouds. `pack.mcmeta` lists no overlays any more: every file has the same path and size on all
  four versions.
- **Swords**: a symmetric three-stripe blade (light flanks, mid centre line, pale glint cells) and an outline in a
  darker shade of the material instead of black. Diamond is blue (`#3f98dc` body), netherite a dusty violet
  (`#4a3566`), gold orange-red (`#c25721`), then wooden, stone and iron in their own colours.
- **Diamond tools**: bright cyan heads (`TOOL_FILL`) with a blue outline.
- **Armor**: netherite is now dark grey-violet (`#312836` mid, `#4a4252` lit) and diamond a clean aqua; layouts unchanged.
- **Ender pearl**: black-green core in a dark-teal ring. **Totem**: tan body, pale face, green outline, green eyes
  and a small green chest gem (the 0.3.0 gold frame is gone).
- **Fire**: amber flames with a pale core (was orange with a white-hot core); tips stay at row 8, so the overlay still
  covers ~7 % / ~20 % / ~29 % of the screen height at FOV 70 / 90 / 110. `fire_0` and `fire_1` are both low.
- **Cobweb**: a cyan frame (`#14a6ba`) round chunky cyan strands (`#1cd2ea`), 62 % opaque, about half of it open.
- **End crystal**: pale steel-blue frames with a jagged inner edge round a pink-violet core with crimson speckles
  (was cyan frames round a magenta core); the base slab is plain dark grey.
- `tools/preview.py` writes `hotbar`, `items`, `armor`, `crystal-and-web` and `low-fire`.

### Fixed
- The `-static` zip now freezes `fire_0` as well as `fire_1`. 0.3.0 shipped a low `fire_0` but only froze `fire_1`,
  so half of the fire blocks in that zip were still animated.

### Added
- `python tools/generate.py --profile {barebones,full}`. `barebones` is the default; `full` regenerates the 0.3.0
  scope (HUD, every tool and armor material, foods, shield, crossbow, trident, elytra, arrows, XP orbs, bobber, water,
  rain, snow, sun, moon, particles, sounds, models, overlays). The generators for all of those are kept.
- Tests (27 in all): the shipped file list is exactly `BAREBONES` and the writer skips anything else (no HUD, models,
  sounds or overlays); symmetric sword stripes with a three-pixel blade; diamond blue, netherite violet and gold
  orange; coloured, not black, outlines; bright cyan tool heads; the cobweb stays 50-68 % opaque; the crystal frame is
  pale steel, its core pink-violet and its base plain grey; the totem has a green outline and eyes; both fire
  textures are low and amber.
- Docs rewritten for the new scope: `README.md` (what changes, profiles, FAQ), `docs/STYLE.md` (measured palettes and
  coverage figures), `docs/COMPATIBILITY.md`, `docs/TESTING.md` (a 17-row checklist).

### Removed from the default pack (all still available in `--profile full`)
- The whole HUD (hotbar, off-hand slot, selector, bars, armor icons, air bubbles, attack indicators), foods other
  than the apple, shield, crossbow, trident, elytra, arrows, XP orbs, fishing bobber, tools and armor of the other
  materials, sun and moon, water, rain and snow, pumpkin overlay, glint, every particle but `critical_hit`, sounds, and
  every item model (items are vanilla size again, the totem pop and the shield are vanilla).
- The previews `hud`, `entities`, `shield` and `sky`.

### Not changed
- The reference also adjusts oak planks, cobblestone, gravel, stone, netherrack and obsidian. Those changes are too
  subtle in the screenshots to measure, so those blocks stay vanilla.
- The pack has still never been loaded in the game by its author; see [docs/TESTING.md](docs/TESTING.md).

## 0.3.0 - restyle: bold colours, no gems, charcoal HUD

Minecraft 1.21.11 - 26.3 (resource-pack formats 75 - 97), unchanged. This release changes the **look**; the file
layout, the version handling and the validator rules are the same as in 0.2.0. The new style follows the overall
look of a PvP pack the owner supplied screenshots of; nothing from that pack is used (all art is generated by the
code, see [docs/STYLE.md](docs/STYLE.md)).

### Changed
- **Tools**: the sword blade is now three pixels wide (lit edge, body, shadow edge, with a dotted glint), the
  other tools keep their shapes. **Diamond tools are blue** and **netherite tools violet**
  (`theme.TOOL_HEADS`); the cyan gem on every handle is gone.
- **Armor** (icons and worn textures): no gems, rivets or buckle studs; calmer plate with a lit and a shadow edge and
  only a trace of speckle. Netherite is near-black violet, diamond bright aqua.
- **HUD**: neutral charcoal hotbar and off-hand slots with a light-grey frame round every slot (was navy), a white
  selector ring with a cyan inner line (was all cyan), white armor icons, a visible grey for empty armor, round
  air bubbles (the old ones looked like snowflakes), neutral attack indicators and bar backgrounds.
- **First person**: items are drawn at **vanilla size** again (0.1 / 0.2 shrank tools to 0.50). Only the shield
  (0.90) and the totem pop (0.50) stay small. A model whose scale equals vanilla's is no longer written, so
  `item/handheld`, `generated`, `bow`, `crossbow`, `handheld_mace` and `spear_in_hand` are not shipped any more.
- **Low fire**: orange tips with a small white-hot core instead of a yellow-amber ramp, tips lowered from row 7 to
  row 8 (average cover of the screen: ~7 % at FOV 70, ~20 % at FOV 90, ~29 % at FOV 110), and `fire_0` now gets
  the same flame as `fire_1`, so world fire is low on both of vanilla's variants.
- **Cobweb**: a 1-px cyan frame with brighter corners round the eight spokes and the ring (was a thin white web).
- **End crystal**: cyan glass frames with near-white corner caps round the magenta core (the frames were magenta).
- **Shield**: oak planks, iron rim, straps and a round boss (was navy steel with a cyan gem).
- **Totem**: green face and an emerald chest gem in a gold frame.
- **Entities**: white-fletched arrow (was cyan), plain red-and-white bobber, silver clasp on the elytra, steel studs on
  the trident and crossbow; the trident and elytra keep their cyan rings / rim.
- **Sky**: the sun is a plain white square with a soft halo (was amber).

### Added
- `docs/STYLE.md`: the palette, the silhouettes and the reasoning behind the look.
- Tests for the new look: neutral hotbar, white selector, blue / violet tools, no gem colours on tools, armor and
  the totem, a three-pixel sword blade, cyan cobweb and crystal frames, low flames in both fire textures, and
  "only changed models ship".

## 0.2.0 - worn armor, entities, food

Minecraft 1.21.11 - 26.3 (resource-pack formats 75 - 97), unchanged.

### Added
- **Worn armor** for copper, chainmail, iron, gold, diamond and netherite (both humanoid layers), in the same
  bevelled-plate style as the inventory icons with the cyan signature gem. Silhouettes match vanilla's.
- **Entity skins**: arrow (cyan and white fletching), tint-friendly tipped arrow, golden spectral arrow, trident
  (3D skin and inventory icon), XP orbs about 38 % smaller, fishing bobber, end crystal (frames, core, base).
- **Icons**: crossbow (standby, three pull stages, arrow loaded, firework loaded) and 17 foods - raw and
  cooked beef, porkchop, mutton, chicken, salmon and cod, plus golden carrot, carrot, bread, baked potato, apple.
- **Elytra**: worn wings plus the inventory and broken icons (navy membrane, cyan rim, shoulder gem).
- **Thin cobweb**: eight spokes and one ring.
- `docs/previews/armor.png` and `docs/previews/entities.png` mock-ups; both versions' overlays now also carry the
  trident, tipped/spectral arrow, XP-orb and bobber textures that moved in 26.1.
- Tooling: `tools/sushantlite/uv.py` (box UV unwrap shared by the shield, armor and entity generators) and
  `tools/tests/` (regression tests: UV rules, armor coverage, texture sizes, tint neutrality, cutout alpha, the
  `--only` overlay fix), run in CI.

### Fixed
- `generate.py --only ...` no longer drops the overlay entries from `pack.mcmeta` (the overlay list is now computed
  from the previous manifest as well as from the files written in that run).

### Not changed on purpose
- Leather (dyeable) and turtle-shell armor and the 26.1+ baby-sized armor are still vanilla.

## 0.1.0 - first release

- Low fire, no pumpkin overlay, clear water and underwater view, thin rain and snow, hidden explosion / smoke /
  sweep particles, quiet explosions, no cave ambience, cyan enchantment glint.
- Smaller first-person items, shield and totem pop; custom shield skin (per-version overlays).
- Full HUD (hotbar, crosshair, hearts in every status, food, armor, air, XP, horse jump).
- Sword / axe / pickaxe / shovel / hoe / spear in seven materials, armor icons, mace, bow, arrow, totem, golden and
  enchanted apples, ender pearl, end crystal, XP bottle, three potions; custom sun, moon phases, clouds; pack icon.
- Tooling: generator, validator (against 1.21.11, 26.1.2, 26.2, 26.3), reproducible zip builder, preview renderer, CI.
