# In-game test checklist

SushantLite is validated structurally by `tools/validate.py`, but it has **not been played yet**.
Use this list to check a build on each target version (1.21.11, 26.1.2, 26.3) and report anything off.

**Install a dev build:** `python tools/build.py`, then copy `dist/SushantLite-vX.Y.Z.zip` into
`.minecraft/resourcepacks/` (or symlink the `SushantLite/` folder there). After editing, press
**F3 + T** in game to reload resources.

| # | Check | How | If it looks wrong |
|---|---|---|---|
| 1 | Pack loads, no red "incompatible" label | Options -> Resource Packs | check the version's format against `docs/COMPATIBILITY.md` |
| 2 | HUD | survival world, take damage, eat, dive | sprite sizes are validated; report visuals |
| 3 | **Low fire** | stand in fire / lava (creative: flint & steel, or `/summon lightning_bolt`); try FOV 70, 90, 110 | `FIRE_TIP_ROW` in `gen/effects.py` (higher number = lower fire) |
| 4 | Pumpkin overlay gone | wear a carved pumpkin | `overlays()` in `gen/effects.py` |
| 5 | Clear water, no underwater tint | dive; look at a shoreline | water alpha in `clear_water()` (~104) |
| 6 | **Shield size/pose** | hold and block, left- and right-handed, on **1.21.11 and 26.x** | `SCALES["shield"]` in `gen/models.py`; 1.21.11 uses the overlay numbers |
| 7 | Shield skin + banner | plain shield, then one with a banner in the crafting grid | `gen/shield.py` |
| 8 | **Totem pop** size | `/give @s totem_of_undying`, hold it, `/damage @s 100` | `SCALES["totem_pop"]` |
| 9 | Item sizes in hand | sword, pickaxe, apple, pearl, potion, bow, mace, spear (`/give @s iron_spear`) | `SCALES` in `gen/models.py` |
| 10 | Items in inventory | all tools, armor icons, potions of several colours, enchanted golden apple | `gen/items.py` |
| 11 | Particles hidden | ignite TNT, burn a block, light a campfire, kill a mob | `particles()` in `gen/effects.py` |
| 12 | Particles that must **still** show | redstone dust, nether portal, dragon breath, crits (tiny), totem | if one is missing, the shared `generic_*` sprites were affected - please report |
| 13 | Sounds | explosion (quieter), cave ambience (silent) | `EXPLOSION_VOLUME` in `gen/sounds.py` |
| 14 | Sky | `/time set midnight`, step through moon phases; look at clouds | `gen/sky.py` |
| 15 | Glint | hold an enchanted item | `glint()` in `gen/effects.py` |
| 16 | Static zip | swap in `-static.zip` | fire/water should be frozen, everything else identical |
| 17 | Logs | open `logs/latest.log`, search `pack`, `Missing`, `Unable` | the only expected message is a harmless "empty soundEvent" for `ambient.cave` |

After changing anything: `python tools/generate.py && python tools/validate.py && python tools/build.py`.
