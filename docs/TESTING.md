# In-game test checklist

SushantLite is validated structurally by `tools/validate.py`, but it has **not been played yet**.
Use this list to check a build on each target version (1.21.11, 26.1.2, 26.3) and report anything off.

Since 0.4.0 the pack is a barebones overlay of 44 files (see `BAREBONES` in `tools/sushantlite/config.py`), so the list
is short. Rows 3, 9, 10 and 11 matter most: they are the things the pack exists for.

**Install a dev build:** `python tools/build.py`, then copy `dist/SushantLite-vX.Y.Z.zip` into
`.minecraft/resourcepacks/` (or symlink the `SushantLite/` folder there). After editing, press
**F3 + T** in game to reload resources.

| # | Check | How | If it looks wrong |
|---|---|---|---|
| 1 | Pack loads, no red "incompatible" label | Options -> Resource Packs | check the version's format against `docs/COMPATIBILITY.md` |
| 2 | **Everything else is vanilla** | survival world: hotbar, hearts, food, XP bar, off-hand slot, buckets, shield, crossbow, trident, elytra, arrows, rain, sun and moon. Compare with a run without the pack if in doubt | a file outside `BAREBONES` has been written: `python -m unittest discover -s tools/tests` should already fail |
| 3 | **Swords** | `/give @s wooden_sword` (also stone, iron, golden, diamond, netherite); check the inventory icon and first person. Expect brown, grey, white, orange-red, **blue** and **dusty violet**, each with a lit and a shadow flank and a coloured outline | `sword()` in `gen/items.py`; colours in `TOOL_HEADS` (`theme.py`) |
| 4 | Diamond tools | `/give @s diamond_pickaxe` (also axe, shovel, hoe): bright cyan heads with a blue edge. Netherite and iron tools must still be vanilla | `tool()` in `gen/items.py`, `TOOL_FILL` |
| 5 | **Worn armor** | `/give @s diamond_helmet`, `diamond_chestplate`, `diamond_leggings`, `diamond_boots` (and netherite); wear them, look at yourself with F5 and at an armor stand (`/summon armor_stand`). Check the seams: helmet band, neck, shoulders, belt, boot cuffs | `gen/armor.py` (coverage rules `layer1_regions` / `layer2_regions`, colours in `colour()`) |
| 6 | Armor mix | wear a diamond chestplate with vanilla iron leggings and netherite boots | each piece keeps its own style; no gaps between pieces |
| 7 | Bow | `/give @s bow`, `arrow`; draw the bow slowly and watch the three pull stages | `gen/items.py` (`bow()` and the pulling frames) |
| 8 | Pearl, apples, totem, potions | `/give @s ender_pearl`, `golden_apple`, `apple`, `totem_of_undying`, then `potion`, `splash_potion`, `lingering_potion` with a tinted effect (`/give @s potion[potion_contents={potion:"healing"}]`). The liquid tint must line up with the bottle | `potion_bottle()` and `potion_overlay()` in `gen/items.py` (both share one liquid mask) |
| 9 | **Low fire** | stand in fire / lava (creative: flint & steel, or `/summon lightning_bolt`); try FOV 70, 90, 110. Expect amber-orange flames with pale cores along the bottom edge only. Also place fire blocks: both of vanilla's two variants must look low | `FIRE_TIP_ROW` in `gen/effects.py` (higher number = lower fire); colours `_FIRE_RAMP` / `_FIRE_CORE` |
| 10 | **Cobweb** | place a cobweb, stand in it, look at it from several angles. Expect a cyan frame round a chunky cyan web, about half of it see-through: a trap you can spot from across the room, but still obviously a web | `cobweb_sprite()` in `gen/effects.py` |
| 11 | **End crystal** | `/summon end_crystal ~ ~1 ~` (also with the base slab: `{ShowBottom:1b}`). Expect pale steel-blue frames with a jagged inner edge round a pink-violet core and a plain dark-grey base | `crystal_texture()`, `STEEL`, `CRYSTAL` in `gen/entities.py`; the glass faces must show the core through them |
| 12 | Totem pop | `/give @s totem_of_undying`, hold it, `/damage @s 100`: the pop shows the new totem at vanilla size | `totem()` in `gen/items.py` |
| 13 | Clouds | look at the sky in daylight: noticeably sparser than vanilla | `clouds()` in `gen/sky.py` |
| 14 | Critical hit | jump and hit a mob: a small white spark | `particle/critical_hit.png` (`gen/effects.py`) |
| 15 | Static zip | swap in `-static.zip` | the fire is frozen, everything else identical |
| 16 | Stacking | put SushantLite **above** another resource pack in the list | only the 44 files change, the rest of the other pack shows through |
| 17 | Logs | open `logs/latest.log`, search `pack`, `Missing`, `Unable` | there should be no message about SushantLite |

For a **full** build (`python tools/generate.py --profile full`) the older checks still apply: HUD, pumpkin overlay, clear
water, shield size and pose on **1.21.11 and 26.x**, totem pop, item sizes, hidden particles, sounds, sky, glint, arrows,
trident, elytra, XP orbs, bobber, crossbow, foods. See the 0.3.0 version of this file in the repository history.

After changing anything: `python tools/generate.py && python tools/validate.py --strict && python tools/build.py`.
