# Compatibility notes

Research behind the "one pack, four versions" design. Facts below were read from the
vanilla asset snapshots of [misode/mcmeta](https://github.com/misode/mcmeta) (tags
`<version>-assets`), from each version's `version.json`, and from the resource packs
Mojang bundles inside the client.

## Pack format per version

| Version | Name | Released | Resource pack format |
|---|---|---|---|
| 1.21.11 | Mounts of Mayhem | 2025-12-09 | 75.0 |
| 26.1 / 26.1.1 / 26.1.2 | Tiny Takeover | 2026-03-24 / 04-01 / 04-09 | 84.0 |
| 26.2 | Chaos Cubed | 2026-06-16 | 88.0 |
| 26.3 | Wilderness Bound | 2026-09-15 | 97.1 |

## `pack.mcmeta`

```json
{ "pack": { "description": [...], "min_format": 75, "max_format": 97 } }
```

* Since 1.21.9 (25w31a) `min_format` / `max_format` replace `pack_format` / `supported_formats`.
  An integer `max_format` means "any minor version of that major", so `97` covers 97.0 and 97.1.
* The pack does not support anything older than format 65, so `pack_format` and
  `supported_formats` are deliberately **absent** (the validator errors on `supported_formats`).
* Cross-check: the built-in `programmer_art.zip` shipped in the 26.1.2 client uses
  `{"min_format": 77, "max_format": 84}` and the 26.3 one `{"min_format": 97, "max_format": 97}` -
  no `pack_format`, no `supported_formats`.
* Overlays: `overlays.entries[]` take `directory`, `min_format` and `max_format` (`formats` only for
  packs that also support pre-1.21.9 versions). Real recent packs that span 1.21.x - 26.3 use the same
  entries, e.g. one with per-version folders for 1.21.11, 26.2 and 26.3, and one with a `_26.1_shaders`
  overlay declared as formats 84-96 (which also confirms 26.1 = format 84).

## What differs between the versions (resource-pack relevant)

Compared with the file lists of the four snapshots:

| Change | Affects SushantLite? |
|---|---|
| **1.21.11 -> 26.1**: many entity textures moved into per-entity folders - `entity/shield_base*.png` -> `entity/shield/shield_base*.png`, `entity/trident*.png` -> `entity/trident/`, `entity/projectiles/{tipped,spectral}_arrow.png` -> `arrow_tipped.png` / `arrow_spectral.png`, `entity/experience_orb.png` -> `entity/experience/`, `entity/fishing_hook.png` -> `entity/fishing/`, plus most mob textures | **Yes, for the shield** - the shield skin is written to both paths via the version overlays (`overlay_1_21_11` for formats 75-83, `overlay_26_1` for 84+; declared in `config.OVERLAYS`). Trident, arrows, XP orb etc. are not retextured yet; they will use the same mechanism. |
| 26.1: `models/item/shield.json` first-person y-translations 2 -> 1.75 and 5 -> 3.25; `items/shield.json` and `items/trident.json` gained a `transformation` (scale 1,-1,-1) | Yes - `shield.json` / `shield_blocking.json` ship twice: the 26.1+ numbers in the base layer and the exact 1.21.11 numbers in `overlay_1_21_11`, so the shield keeps the same pose on every version. |
| 26.1 -> 26.2: sign and bed textures/models moved; core text shaders removed | No. (Also why text-shader tweaks are not portable.) |
| 26.2 -> 26.3: armor-trim palettes restructured, `item/light` removed, cloud / world-border / transparency shaders removed | No. |
| **Unchanged across all four**: every HUD sprite, item texture, particle texture and definition used here, `environment/` (sun, moon, clouds, rain, snow), `block/fire_*`, `block/water_*`, `misc/*` overlays, and the `generated`, `handheld`, `handheld_mace`, `bow`, `crossbow`, `spear_in_hand`, `totem_of_undying` item models | Yes - these form the shared base in `SushantLite/assets`. |
| `sounds.json` differs per version (new events) | The pack lists only two events (`ambient.cave`, `entity.generic.explode`); sample names were verified identical on all four versions. |

Rule enforced by `tools/validate.py`: everything in `SushantLite/assets` must be valid on **every**
supported version; anything version-specific lives in an overlay whose format range matches.

## How the first-person fire overlay samples `fire_1.png`

Used to design the low-fire sprite (and to render `docs/previews/low-fire.png`):

* two 1x1 quads at depth 0.5, centred at x = +-0.24, moved down by 0.3, colour alpha 0.9;
* each quad maps only the **middle 75 %** of the 16x16 frame (v from 1/8 to 7/8);
* at the default FOV 70 the screen shows roughly sprite rows 2 -> 8.6, at FOV 110 rows 2 -> 13.

So vanilla flame tips (around row 2) reach 65-80 % of the screen height, whereas tips at row ~7
with a translucent body below give a fire that sits in the bottom quarter-to-third.

## Audit of the item-model overrides

Each overridden model was diffed key-by-key against the vanilla file on 1.21.11 and 26.3
(`generated`, `handheld`, `handheld_mace`, `bow`, `crossbow`, `spear_in_hand`, `shield`,
`shield_blocking`, `totem_of_undying`, `enchanted_golden_apple`). The only differences are the
first-person `scale` values (plus the totem's added `fixed` transform, the enchanted apple's texture
reference, and the shield translation that is deliberately version-specific). No key is dropped.

## Verified vs. not verified

**Verified by tooling** (`tools/validate.py`, run on every build and in CI):

* every override exists on each supported version with the same dimensions (animation strips:
  same width, whole frames);
* `.mcmeta` files sit next to their PNG and reference valid frames;
* item-model parents/textures resolve, display transforms are finite and in range;
* particle sprites resolve (custom sprites must live in `textures/particle/`);
* sound events exist; `pack.mcmeta` and overlay rules hold; file names are lowercase-safe.

**Not verified** (needs the game):

* how everything *looks* in first person - the sizes in `models.py` and the fire height are
  informed estimates; tune them in-game;
* the `poof` / `smoke` / `large_smoke` re-pointing relies on the particle atlas stitching
  `textures/particle/sushantlite_blank.png` (it stitches every PNG in that directory in vanilla);
* the empty-`sounds` override for `ambient.cave` (may log a harmless "empty sound event" warning).
