# Changelog

All notable changes to SushantLite. Versions follow `tools/sushantlite/config.py` (`PACK_VERSION`);
the supported Minecraft range is listed per release. Neither release has been played in the game yet;
see [docs/TESTING.md](docs/TESTING.md).

## 0.2.0 - worn armor, entities, food

Minecraft 1.21.11 - 26.3 (resource-pack formats 75 - 97), unchanged.

### Added
- **Worn armor** for copper, chainmail, iron, gold, diamond and netherite (both humanoid layers), in the same
  bevelled-plate style as the inventory icons with the cyan signature gem. Silhouettes match vanilla's.
- **Entity skins**: arrow (cyan and white fletching), tint-friendly tipped arrow, golden spectral arrow, trident
  (3D skin and inventory icon), XP orbs about 38 % smaller, fishing bobber, end crystal (frames, core, base).
- **Icons**: crossbow (standby, three pull stages, arrow loaded, firework loaded) and 17 foods - raw and
  cooked beef, porkchop, mutton, chicken, salmon and cod, plus golden carrot, carrot, bread, baked potato, apple.
- **Thin cobweb**: eight spokes and one ring.
- `docs/previews/armor.png` and `docs/previews/entities.png` mock-ups; both versions' overlays now also carry the
  trident, tipped/spectral arrow, XP-orb and bobber textures that moved in 26.1.
- Tooling: `tools/sushantlite/uv.py` (box UV unwrap shared by the shield, armor and entity generators).

### Fixed
- `generate.py --only ...` no longer drops the overlay entries from `pack.mcmeta` (the overlay list is now computed
  from the previous manifest as well as from the files written in that run).

### Not changed on purpose
- Leather (dyeable) and turtle-shell armor, the elytra and the 26.1+ baby-sized armor are still vanilla.

## 0.1.0 - first release

- Low fire, no pumpkin overlay, clear water and underwater view, thin rain and snow, hidden explosion / smoke /
  sweep particles, quiet explosions, no cave ambience, cyan enchantment glint.
- Smaller first-person items, shield and totem pop; custom shield skin (per-version overlays).
- Full HUD (hotbar, crosshair, hearts in every status, food, armor, air, XP, horse jump).
- Sword / axe / pickaxe / shovel / hoe / spear in seven materials, armor icons, mace, bow, arrow, totem, golden and
  enchanted apples, ender pearl, end crystal, XP bottle, three potions; custom sun, moon phases, clouds; pack icon.
- Tooling: generator, validator (against 1.21.11, 26.1.2, 26.2, 26.3), reproducible zip builder, preview renderer, CI.
