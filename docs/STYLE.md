# SushantLite look & feel (since 0.3.0)

Version 0.3.0 restyled the whole pack after the owner asked for it to look like a PvP pack they had found
(five in-game screenshots, from a pack-hosting site). This page records **what that look is** and **how
SushantLite reproduces it**, so the design survives even though the screenshots are not (and must not be)
stored in this repository.

## Provenance, in plain words

* The reference packs on that kind of site are normally marked "All rights reserved". So **nothing was copied**:
  no file, texture or pixel of the reference pack is used, and the generator never reads any pack except the
  vanilla *names and sizes* in `tools/reference/`.
* Only screenshots (3D renders at an angle, partly hidden by the HUD) were available, so the match is by
  *style, colours, proportions and feature set*, drawn from scratch. It is not pixel-identical, and where a detail
  could not be seen it was kept as it was.

## What the reference looked like, and what SushantLite does about it

| Element | What the screenshots showed | SushantLite 0.3.0 |
|---|---|---|
| Hotbar | neutral dark-grey slots with a light-grey frame, the selected slot ringed in white-cyan, the off-hand slot separate on the left | charcoal bar (`#17181c`, 80 %), `#9ea1aa` slot frames, white selector ring with a cyan inner line |
| Hearts, food, XP | classic red hearts, drumsticks, green XP bar | same shapes, neutral containers; air bubbles are round |
| Armor icons | white (full) / dark grey (empty) chestplates | white ramp, `#3a3b43` for empty |
| Diamond sword and tools | **blue**, light-cyan edge, dark outline | `TOOL_HEADS["diamond"]`: `#1b4aa6 / #2d8be4 / #62d1ff / #e6fbff` |
| Netherite sword and tools | **violet** | `TOOL_HEADS["netherite"]`: `#2a1d52 / #5b3fa8 / #9577e6 / #e8dcff` |
| Sword size in first person | full-size blades in both hands | vanilla scale (0.68) for all tools |
| Worn armor | bright aqua diamond, near-black violet netherite, white iron, yellow gold, grey mesh chainmail, brown leather | same colours; clean plate, no gems; leather stays vanilla |
| Totem | gold body with a green face | gold frame, green face, emerald chest gem |
| Shield (hotbar icon) | brown wood with a dark rim | oak planks, iron rim, straps and boss |
| Cobweb | thick **cyan** frame with a white-cyan web | 1-px cyan frame, brighter corners, eight spokes + ring |
| End crystal | **cyan / white** frames round a magenta core | cyan frame with near-white corner caps, magenta core |
| Fire (on screen) | very low, chunky **orange** cells with white spots at both bottom corners | orange tips with white-hot cores, average cover 7-29 % of the screen height, both fire textures |
| Sun | plain white square | white square with a soft halo |
| Ender pearl, golden apple, potions, bow, end-crystal item | dark outline, saturated colours | unchanged shapes (already close), no cyan decoration |

Not visible in the screenshots, therefore **left as they were**: container GUIs, most blocks (ores, obsidian,
leaves ...), mobs, sounds, particles, rain and snow.

## Palette

| Role | Colours |
|---|---|
| Outline | `#0a0b0f` (all item sprites), `#07080a` (HUD) |
| HUD panel | fill `#17181c`, frame `#9ea1aa`, inner shadow `#25262b`, bar top `#4b4d55` |
| Accent (frames, glint, selector line) | `#38e1ff` dark `#1789ad` light `#c9f7ff` |
| Cobweb | frame `#22c6e8`, corner caps `#b9f6ff`, thread `#eafdff`, ring `#7fe0f5` |
| End crystal | glass frame `#2fc8ec`, caps `#d4f9ff`, core ramp `#5d1a86 / #b247dc / #ec8bff / #ffe7ff` |
| Fire | tips `#ffa826` -> body `#bb390e`, core `#fff1b8 / #ffd966 / #ffb73a` |
| Armor (worn + icons) | diamond `#14a2b4 / #37dccf / #8ff7ed`, netherite `#16111e / #2b2338 / #4a3e68 / #8c7abd`, iron `#97a3ad / #d2dae0`, gold `#d08c0c / #ffc72c` |

## Rules of thumb used by the generators

* **Vanilla proportions, bolder colours.** Silhouettes follow the usual 16x16 conventions (a diagonal blade, a
  guard, a short grip); the sword blade is three pixels wide so first person shows a lit edge, a body and a
  shadow edge.
* **No decoration pixels** (gems, studs, rivets) on tools, armor, the totem or the bow; cyan is only used for
  frames, glow rings and the glint.
* **Binary alpha** on every cutout texture (entities, cobweb), because cutout render types discard partial alpha.
* **Neutral HUD**: every pixel of the hotbar and off-hand sprites keeps its channels within 14 of each other (a test enforces it).

## Knobs

| Want to change ... | Edit |
|---|---|
| Diamond / netherite tool colours | `TOOL_HEADS`, `TOOL_TRIM` in `tools/sushantlite/theme.py` |
| Armor colours | `MATERIALS`, `TRIM` in the same file |
| HUD greys | `INK`, `EDGE_OUT`, `EDGE_IN`, `SLOT_DARK` in `tools/sushantlite/gen/hud.py`; `PANEL*` in `theme.py` |
| Fire height and colours | `FIRE_TIP_ROW`, `_FIRE_RAMP`, `_FIRE_CORE` in `gen/effects.py` |
| First-person sizes | `SCALES` in `gen/models.py` |
