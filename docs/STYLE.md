# SushantLite look & feel (since 0.4.0)

0.4.0 re-scoped the whole pack after the owner said that 0.2.0 and 0.3.0 looked different from the pack they wanted
**in everything**. The pack they pointed at is *Barebones PvP Overlay 16x* (BaseballBeans, on a pack-hosting site),
shown in five in-game screenshots. This page records **what that look is** and **how SushantLite reproduces it**, so the
design survives even though the screenshots are not (and must not be) stored in this repository.

## Provenance, in plain words

* The reference is marked **"All rights reserved"**. So **nothing was copied**: no file, texture or pixel of it is used,
  and the generator never reads any pack except the vanilla *names and sizes* in `tools/reference/`.
* What was used: the owner's five screenshots, looked at to decide **which things differ from vanilla**, and a k-means
  colour sampler run over them to get **palettes** (hex colours) and **coverage figures** (how much of the screen the
  fire fills). Only those numbers went into the code. The screenshots, the crops and the sampler are not stored here.
* The match is therefore by *scope, colours, proportions and style*, with every texture drawn from scratch. It is **not
  pixel-identical**, and where a detail could not be seen it was kept plain. The only way to get the original textures
  is the original pack: it can be placed *above* SushantLite in the resource-pack list, and because SushantLite is a
  small overlay the two stack without conflict.

## The lesson of 0.2.0 and 0.3.0: scope matters more than art

Those releases redrew everything the generators could draw (a charcoal HUD, hearts and food, shield, crossbow, XP orbs,
water, rain, sun and moon, particles, smaller first-person items ...). The screenshots show a **vanilla** HUD, vanilla
hearts and food, a vanilla XP bar, vanilla buckets and item frames. A pack that restyles them looks different in every
screenshot, which is exactly what the owner reported. So the rule since 0.4.0 is:

> **Ship only what the reference changes. Leave everything else exactly as Mojang made it.**

The list of shipped files is `BAREBONES` in `tools/sushantlite/config.py`, enforced by `PackWriter` and by a test.

## What the reference looked like, and what SushantLite does about it

| Element | What the screenshots showed | SushantLite 0.4.0 |
|---|---|---|
| Hotbar, hearts, food, armor bar, XP bar, crosshair | completely vanilla | **not touched** |
| Buckets, fishing rod, shield, crossbow, trident, elytra, arrows, XP orbs, bobber, other tools and armor | vanilla | **not touched** |
| Diamond sword | blue, symmetric stripes: first person `#51b7f7` / `#4194db` / `#203c9a`, hotbar icon `#5ad8fb` / `#48a2d6` / `#2967ae` | `TOOL_HEADS["diamond"]`: `#2358b4 / #3f98dc / #5ad8fb / #c4f7ff`, outline `#173975` |
| Netherite sword | dusty violet: first person `#211136` / `#3e2756` / `#544269`, hotbar `#4e3562` / `#6d5479` | `TOOL_HEADS["netherite"]`: `#2a1a3e / #4a3566 / #6d5a90 / #a090c0`, outline `#1b1128` |
| Gold, iron, stone, wooden swords | same blade shape, each in its own material colour | golden `#8e3a12 / #c25721 / #e8803a / #ffc890`; wooden, stone and iron from `MATERIALS` |
| Diamond pickaxe, axe, shovel, hoe | bright cyan heads (`#5bf3fd`) with a blue outline (`#205497`) | `TOOL_FILL["diamond"]`: `#2a74c8 / #55d4fa / #98f4ff / #e0fdff` |
| Worn armor | aqua diamond (`#30b4ac`, lit `#259c92`), near-black violet netherite (`#2f2534`, lit `#453e4d`) | `MATERIALS` / `TRIM` in `theme.py`: diamond `#14a2b4 / #37dccf / #8ff7ed`, netherite `#1d1822 / #312836 / #4a4252 / #6d6477` |
| Ender pearl | dark-teal ring round a black-green core (`#042b17 / #045841 / #207e60 / #3ba784 / #78c5aa`) | those five colours, a glint on the upper-left rim |
| Totem | tan body (`#c6a35c` / `#976128`), pale face (`#e5d484`), green outline (`#33811c`) | the same, green eyes and a small green chest gem as in vanilla |
| Golden apple, apple, bow, potions | dark outline, saturated colours | same shapes, dark outlines; potions share one liquid mask with `potion_overlay` |
| Cobweb | thick **cyan** frame, chunky web, about half of it open (`#1cd2ea`, frame and shade `#14a6ba` / `#127c87`) | 62 % opaque: frame, eight spokes (2 px cardinal, 1 px diagonal), one ragged ring, a solid hub |
| End crystal | pale steel-blue frames (`#d7e5f6 / #b4c7e0 / #9eabc0 / #8392a1`) with a jagged inner edge round a pink-violet core (`#d47ff1 / #c470e1 / #b769c7 / #80448c / #6a2256`) | frames and core in those colours, crimson speckles on the core, a plain dark-grey base |
| Fire (on screen) | very low, chunky amber and orange cells with a pale core (blended: `#cf7e0f`, `#d58d1c`, `#e0a92d`, `#f3d068`, `#ffec97`) | `_FIRE_RAMP` / `_FIRE_CORE` in `gen/effects.py`; tips at row 8, so the overlay covers about 7 % (FOV 70), 20 % (FOV 90), 29 % (FOV 110) of the screen height |
| Clouds, critical hit | sparser clouds, a tiny spark | ~23 % cloud coverage, a small white spark |

The reference also adjusts a few blocks (oak planks, cobblestone, gravel, stone, netherrack, obsidian). Their changes are
too subtle in the screenshots to measure (obsidian, for example, was `#04020b` with `#2d1944` flecks, which is vanilla),
so they are **left vanilla** rather than guessed.

## Palette quick reference

| Role | Colours |
|---|---|
| Sword outlines | the material's dark shade at 65 % brightness (`outline_for()` in `gen/items.py`) - never black |
| Diamond ramp (blade / head) | `#2358b4 / #3f98dc / #5ad8fb / #c4f7ff`; head fill `#2a74c8 / #55d4fa / #98f4ff / #e0fdff` |
| Netherite ramp | `#2a1a3e / #4a3566 / #6d5a90 / #a090c0` |
| Cobweb | web `#1cd2ea`, glint `#6fe6f6`, frame `#14a6ba` |
| End crystal | frame `#8392a1 / #9eabc0 / #b4c7e0 / #d7e5f6`, core `#5a1f4f / #a04a9a / #c470e1 / #efb4fb`, speckles `#d02a5c` |
| Fire | tips `#f2b236` -> body `#a95206`, core `#fff4c8 / #ffe28a / #f8c850` |

## Rules of thumb used by the generators

* **Symmetric blades.** A sword blade is three pixels wide along the diagonal: a light flank on each side of a mid
  centre line (`x + y = 16`), a pale glint on the tip and on every other cell of the upper flank. That is the stripe
  pattern the first-person screenshots show.
* **Coloured outlines.** Every item outline is a darker shade of the item's own colour; the dark-teal pearl ring, the
  green totem outline and the blue sword edges are what make the reference read as "bold" rather than black.
* **No decoration pixels** (gems, studs, rivets) on tools, armor or the bow. (The totem keeps vanilla's small green
  chest gem.)
* **Chunky, not busy.** The cobweb is meant to stay readable from across a room: 62 % opaque, frame included. The
  first 0.4.0 draft was a 73 % lattice and read as a solid block; a test now keeps it between 50 and 68 %. It is
  never a thin 1-px web either.
* **Binary alpha** on every cutout texture (worn armor, end crystal, cobweb), because cutout render types discard
  partial alpha.
* **Static where possible.** Only `fire_0` and `fire_1` are animated; the `-static` zip freezes them to one frame.

## Knobs

| Want to change ... | Edit |
|---|---|
| Diamond / netherite / golden tool colours | `TOOL_HEADS`, `TOOL_FILL`, `TOOL_TRIM` in `tools/sushantlite/theme.py` |
| Armor colours | `MATERIALS`, `TRIM` in the same file |
| Sword outline darkness | `outline_for()` in `gen/items.py` |
| Fire height and colours | `FIRE_TIP_ROW`, `_FIRE_RAMP`, `_FIRE_CORE` in `gen/effects.py` |
| Cobweb pattern and density | `cobweb_sprite()` in `gen/effects.py` |
| Crystal colours | `STEEL`, `CRYSTAL` in `gen/entities.py` |
| What the pack ships | `BAREBONES` in `tools/sushantlite/config.py` (and `generate.py --profile full` for everything) |
