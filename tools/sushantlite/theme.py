"""SushantLite visual identity: one place to retheme the whole pack.

Change ACCENT (and friends), run ``python tools/generate.py`` and every sprite
that uses the accent colour is redrawn.
"""
from __future__ import annotations

from dataclasses import dataclass

# ------------------------------------------------------------------ brand colours
ACCENT = "#38e1ff"        # electric cyan: selection ring, cobweb + crystal frames, glint (no longer a gem on every item)
ACCENT_DARK = "#1789ad"
ACCENT_LIGHT = "#c9f7ff"
INK = "#0a0b0f"           # universal sprite outline (near-black, a touch cool)
WHITE = "#f4fbff"

# HUD panels: neutral charcoal with a light-grey frame, so the bar reads on any biome
PANEL = "#17181c"
PANEL_EDGE = "#7f828b"
PANEL_ALPHA = 0xCC        # ~80 % opaque

# ------------------------------------------------------------------ materials
@dataclass(frozen=True)
class Ramp:
    """Four-tone colour ramp: dark -> mid -> light -> shine."""
    d: str
    m: str
    l: str
    s: str


MATERIALS: dict[str, Ramp] = {
    "wooden":    Ramp("#7a4e24", "#a8743a", "#c99a5b", "#e8c48f"),
    "stone":     Ramp("#5d646c", "#8a929a", "#b1b9c0", "#dde3e8"),
    "copper":    Ramp("#a2481f", "#dd7a3f", "#fba76d", "#ffd6b0"),
    "iron":      Ramp("#97a3ad", "#d2dae0", "#edf2f5", "#ffffff"),
    "golden":    Ramp("#d08c0c", "#ffc72c", "#ffe66c", "#fff8bd"),
    "diamond":   Ramp("#14a2b4", "#37dccf", "#8ff7ed", "#e4fffb"),
    "netherite": Ramp("#1d1822", "#312836", "#4a4252", "#6d6477"),      # dark grey-violet (measured on the reference armor)
    "chainmail": Ramp("#4f5861", "#7f8a94", "#aab5be", "#d9e0e5"),
}

# Guard / head-socket colours for each material (a darker, more neutral trim)
TRIM: dict[str, Ramp] = {
    "wooden":    Ramp("#4f3216", "#6b4521", "#86592b", "#a0713c"),
    "stone":     Ramp("#434950", "#5f666d", "#7c848b", "#98a0a7"),
    "copper":    Ramp("#7d3414", "#a9501f", "#cc6c33", "#e88a52"),
    "iron":      Ramp("#68737c", "#8c98a2", "#aeb9c2", "#cfd8df"),
    "golden":    Ramp("#a86e06", "#d9960f", "#f2b928", "#ffd75e"),
    "diamond":   Ramp("#0e7886", "#169aa8", "#27bfc4", "#6bdcd9"),
    "netherite": Ramp("#0e0b11", "#1b1620", "#2c2535", "#443c50"),
    "chainmail": Ramp("#363d44", "#4d565e", "#69737c", "#8a959d"),
}

# Tools and swords do not follow the armour colours for three materials: diamond is blue (deep blue
# edge -> azure -> cyan), netherite a dusty violet and gold an orange-red, so they are told apart at a
# glance in the hotbar and in first person.  The ramps were measured on screenshots of the pack this
# look follows (diamond sword: #51b7f7 / #4194db / #203c9a, netherite sword: #6d5479 / #4e3562 /
# #29182e).  Everything else uses MATERIALS / TRIM.
TOOL_HEADS: dict[str, Ramp] = {
    "diamond":   Ramp("#2358b4", "#3f98dc", "#5ad8fb", "#c4f7ff"),
    "netherite": Ramp("#2a1a3e", "#4a3566", "#6d5a90", "#a090c0"),
    "golden":    Ramp("#8e3a12", "#c25721", "#e8803a", "#ffc890"),
}
# The axe / pickaxe / shovel / hoe heads are brighter than the sword blade: a cyan fill (#5bf3fd on the
# reference's axe) with blue shadow edges and a blue outline.
TOOL_FILL: dict[str, Ramp] = {
    "diamond":   Ramp("#2a74c8", "#55d4fa", "#98f4ff", "#e0fdff"),
}
TOOL_TRIM: dict[str, Ramp] = {
    "diamond":   Ramp("#13284f", "#1f3c78", "#2f58a4", "#4c7dcc"),
    "netherite": Ramp("#170f27", "#271a42", "#3a2a60", "#563f8c"),
    "golden":    Ramp("#6a2a0c", "#963f14", "#c25a1e", "#e07a3a"),
}

HANDLE = Ramp("#583717", "#7d5226", "#a47036", "#c18d4e")   # classic stick

MATERIAL_ORDER = ["wooden", "stone", "copper", "iron", "golden", "diamond", "netherite"]   # tools
ARMOR_ORDER = ["copper", "chainmail", "iron", "golden", "diamond", "netherite"]                  # armour

# ------------------------------------------------------------------ misc palettes
RED = Ramp("#a3142b", "#e4283f", "#ff6478", "#ffc1c9")
GOLD = MATERIALS["golden"]
GREEN = Ramp("#2c8a2a", "#52cc3b", "#97ee6a", "#d6ffb8")
ORANGE = Ramp("#b5531b", "#f0832a", "#ffb04f", "#ffe0a8")
PURPLE = Ramp("#4a1f86", "#8a46dd", "#bc83ff", "#e9d4ff")
STEEL = Ramp("#46505c", "#6f7c8a", "#9aa8b6", "#c9d4de")
NAVY = Ramp("#1b2540", "#2d3b60", "#4a5f93", "#9fb2d6")    # deep blue steel: shield, trident, elytra
