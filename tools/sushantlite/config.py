"""Central configuration for the SushantLite build tooling.

Everything that is "a decision about the pack" lives here, so bumping the
supported game versions or the pack version is a one-line change.
"""
from __future__ import annotations

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
PACK_VERSION = "0.1.0"
PACK_TAGLINE = "PvP-lite 16x"

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
