"""Central configuration for the SushantLite build tooling.

Everything that is "a decision about the pack" lives here, so bumping the
supported game versions or the pack version is a one-line change.
"""
from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = ROOT / "tools"
REFERENCE_DIR = TOOLS_DIR / "reference"
PACK_NAME = "SushantLite"
PACK_DIR = ROOT / PACK_NAME            # the actual resource pack (what gets zipped)
DIST_DIR = ROOT / "dist"
DOCS_DIR = ROOT / "docs"
GENERATED_MANIFEST = TOOLS_DIR / "generated-files.txt"   # files owned by the generator
LOCKED_FILE = TOOLS_DIR / "locked.txt"                   # hand-edited files the generator must not touch

# --------------------------------------------------------------------------- #
# Pack identity
# --------------------------------------------------------------------------- #
PACK_VERSION = "0.4.0"
PACK_TAGLINE = "PvP overlay 16x"

# --------------------------------------------------------------------------- #
# Scope ("profile")
#
# 0.4.0 follows the pack the owner asked for: a *barebones overlay* that changes a handful of PvP
# textures and leaves everything else (the whole HUD, food, shield, tools of other materials, water,
# weather, sounds ...) exactly as vanilla.  The generators still draw every texture the project has
# ever had, but the PackWriter only writes the files listed in BAREBONES unless the "full" profile
# is selected (``python tools/generate.py --profile full``, or SUSHANTLITE_PROFILE=full).
# --------------------------------------------------------------------------- #
PROFILE = os.environ.get("SUSHANTLITE_PROFILE", "barebones")

_ITEM = "assets/minecraft/textures/item"
_EQUIP = "assets/minecraft/textures/entity/equipment"
_BLOCK = "assets/minecraft/textures/block"
SWORD_MATERIALS = ("wooden", "stone", "iron", "golden", "diamond", "netherite")

BAREBONES: frozenset[str] = frozenset({
    "pack.mcmeta", "pack.png",
    # weapons and tools
    *(f"{_ITEM}/{m}_sword.png" for m in SWORD_MATERIALS),
    *(f"{_ITEM}/diamond_{t}.png" for t in ("pickaxe", "axe", "shovel", "hoe")),
    f"{_ITEM}/bow.png", *(f"{_ITEM}/bow_pulling_{i}.png" for i in range(3)),
    # armor: icons and worn textures for the two top tiers
    *(f"{_ITEM}/{m}_{p}.png" for m in ("diamond", "netherite") for p in ("helmet", "chestplate", "leggings", "boots")),
    *(f"{_EQUIP}/{layer}/{m}.png" for layer in ("humanoid", "humanoid_leggings") for m in ("diamond", "netherite")),
    # PvP consumables
    f"{_ITEM}/ender_pearl.png", f"{_ITEM}/golden_apple.png", f"{_ITEM}/apple.png", f"{_ITEM}/totem_of_undying.png",
    *(f"{_ITEM}/{n}.png" for n in ("potion", "splash_potion", "lingering_potion", "potion_overlay")),
    # world and effects
    f"{_BLOCK}/cobweb.png",
    *(f"{_BLOCK}/fire_{i}.png{ext}" for i in (0, 1) for ext in ("", ".mcmeta")),
    "assets/minecraft/textures/entity/end_crystal/end_crystal.png",
    "assets/minecraft/textures/particle/critical_hit.png",
    "assets/minecraft/textures/environment/clouds.png",
})


def included(rel: str) -> bool:
    """Does the active profile ship this pack-relative file?"""
    return PROFILE == "full" or rel in BAREBONES


# --------------------------------------------------------------------------- #
# Supported game versions (Java Edition)
#
# Resource pack formats come straight from each version's version.json:
#   1.21.11 -> 75.0    26.1.x -> 84.0    26.2 -> 88.0    26.3 -> 97.1
#
# `min_format` / `max_format` replaced `pack_format` in 1.21.9 (25w31a).  An
# integer `max_format` means "any minor version of that major", so 97 covers
# 97.0, 97.1 ...  Bump MAX_FORMAT (and re-run the validator) for new versions.
# --------------------------------------------------------------------------- #
MIN_FORMAT = 75      # 1.21.11
MAX_FORMAT = 97      # 26.3

# The pack stores version-specific files in overlays.  Everything in
# `<pack>/assets` must be valid on *every* supported version; anything that
# moved between versions lives in an overlay whose format range matches.
#
# name -> (min_format, max_format)
OVERLAYS: dict[str, tuple[int, int]] = {
    "overlay_1_21_11": (MIN_FORMAT, 83),   # 1.21.11 (format 75 .. 83)
    "overlay_26_1": (84, MAX_FORMAT),      # 26.1 and newer (format 84 ..)
}

# --------------------------------------------------------------------------- #
# Vanilla reference snapshots (used for validation only, never shipped)
# --------------------------------------------------------------------------- #
# Source: https://github.com/misode/mcmeta  (tag "<version>-assets")
REFERENCE_VERSIONS = ["1.21.11", "26.1.2", "26.2", "26.3"]
MCMETA_REPO = "https://github.com/misode/mcmeta.git"
