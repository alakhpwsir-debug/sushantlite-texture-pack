# In-game test checklist

SushantLite is validated structurally by `tools/validate.py`, but it has **not been played yet**.
Use this list to check a build on each target version (1.21.11, 26.1.2, 26.3) and report anything off.

**Version 0.3.0 changed the look**, so check rows 2, 3, 7, 9, 10, 17, 21, 26 and 27 first.

**Install a dev build:** `python tools/build.py`, then copy `dist/SushantLite-vX.Y.Z.zip` into
`.minecraft/resourcepacks/` (or symlink the `SushantLite/` folder there). After editing, press
**F3 + T** in game to reload resources.

| # | Check | How | If it looks wrong |
|---|---|---|---|
| 1 | Pack loads, no red "incompatible" label | Options -> Resource Packs | check the version's format against `docs/COMPATIBILITY.md` |
| 2 | HUD | survival world, take damage, eat, dive | sprite sizes are validated; report visuals |
| 3 | **Low fire** | stand in fire / lava (creative: flint & steel, or `/summon lightning_bolt`); try FOV 70, 90, 110. Expect orange flames with a few white-hot spots along the bottom edge only. Also place fire blocks: both of vanilla's two variants must look low | `FIRE_TIP_ROW` in `gen/effects.py` (higher number = lower fire); colours `_FIRE_RAMP` / `_FIRE_CORE` |
| 4 | Pumpkin overlay gone | wear a carved pumpkin | `overlays()` in `gen/effects.py` |
| 5 | Clear water, no underwater tint | dive; look at a shoreline | water alpha in `clear_water()` (~104) |
| 6 | **Shield size/pose** | hold and block, left- and right-handed, on **1.21.11 and 26.x** | `SCALES["shield"]` in `gen/models.py`; 1.21.11 uses the overlay numbers |
| 7 | Shield skin + banner | plain shield (oak planks, iron rim, straps, round boss), then one with a banner in the crafting grid | `gen/shield.py` |
| 8 | **Totem pop** size | `/give @s totem_of_undying`, hold it, `/damage @s 100` | `SCALES["totem_pop"]` |
| 9 | Item sizes in hand | sword, pickaxe, apple, pearl, potion, bow, mace, spear (`/give @s iron_spear`): all vanilla size except the shield. Compare with a vanilla install if in doubt | `SCALES` in `gen/models.py` (lower a value to shrink that group) |
| 10 | Items in inventory and in first person | diamond tools should be **blue**, netherite tools **violet**; the sword blade is a bold three-tone shape | `gen/items.py`, `TOOL_HEADS` in `theme.py` |
| 11 | Particles hidden | ignite TNT, burn a block, light a campfire, kill a mob | `particles()` in `gen/effects.py` |
| 12 | Particles that must **still** show | redstone dust, nether portal, dragon breath, crits (tiny), totem | if one is missing, the shared `generic_*` sprites were affected - please report |
| 13 | Sounds | explosion (quieter), cave ambience (silent) | `EXPLOSION_VOLUME` in `gen/sounds.py` |
| 14 | Sky | `/time set midnight`, step through moon phases; look at clouds | `gen/sky.py` |
| 15 | Glint | hold an enchanted item | `glint()` in `gen/effects.py` |
| 16 | Static zip | swap in `-static.zip` | fire/water should be frozen, everything else identical |
| 17 | **Worn armor** | `/give @s iron_helmet`, `iron_chestplate`, `iron_leggings`, `iron_boots` (also copper, chainmail, golden, diamond, netherite); wear them, then look at yourself with F5 and at a second player or an armor stand (`/summon armor_stand`). Check the seams: helmet band, neck, shoulders, belt, boot cuffs | `gen/armor.py` (coverage rules `layer1_regions` / `layer2_regions`, colours in `colour()`) |
| 18 | Armor mix | wear a netherite chestplate with diamond leggings and gold boots | each piece should keep its own style; no gaps between pieces |
| 19 | **Arrows** | shoot a normal arrow, a tipped arrow (`/give @s tipped_arrow[potion_contents={potion:"swiftness"}]`) and a spectral arrow | tipped arrows should take the potion's colour all over; `gen/entities.py` (`ARROW`, `TIPPED`, `SPECTRAL`) |
| 20 | Trident | `/give @s trident`, hold it, throw it | `trident_texture()` in `gen/entities.py` |
| 20b | Elytra | `/give @s elytra`; wear it and look at yourself from behind (F5), then glide; also check the broken icon (`/give @s elytra[damage=431]`) | `gen/wings.py` (`_wing_cells`, `wing_texture`) |
| 21 | **End crystal** | `/summon end_crystal ~ ~1 ~` (also with the base slab: `{ShowBottom:1b}`). Expect a cyan frame with white corners round a magenta core | `crystal_texture()` in `gen/entities.py`; glass faces must show the core through them |
| 22 | XP orbs | `/summon experience_orb ~ ~1 ~ {Value:3}`, then `{Value:50}` and `{Value:500}` | `ORB_RADII` in `gen/entities.py` |
| 23 | Fishing bobber | cast a fishing rod into water | `bobber_texture()` |
| 24 | Crossbow icons | `/give @s crossbow`, `arrow`, `firework_rocket`; charge it, load each | `gen/ranged.py` |
| 25 | Foods | `/give @s cooked_beef` ... (see the list in the README), hotbar and inventory | `gen/food.py` |
| 26 | Cobweb | place a cobweb, stand in it, look at it from several angles; it should show a cyan frame and a white-cyan web | `cobweb()` in `gen/effects.py` |
| 27 | HUD look | take damage, eat, wear armor; the hotbar is neutral charcoal with light-grey slot frames, the selected slot has a white ring, empty armor icons are visible grey, air bubbles are round | `gen/hud.py` (`EDGE_OUT`, `INTERIOR`, `selection()`) |
| 28 | Logs | open `logs/latest.log`, search `pack`, `Missing`, `Unable` | the only expected message is a harmless "empty soundEvent" for `ambient.cave` |

After changing anything: `python tools/generate.py && python tools/validate.py && python tools/build.py`.
