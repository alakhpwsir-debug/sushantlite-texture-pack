"""SushantLite visual identity: one place to retheme the whole pack.

Change ACCENT (and friends), run ``python tools/generate.py`` and every sprite
that uses the accent colour is redrawn.
"""
from __future__ import annotations

from dataclasses import dataclass

# ------------------------------------------------------------------ brand colours
ACCENT = "#38e1ff"        # signature electric cyan
ACCENT_DARK = "#1789ad"
ACCENT_LIGHT = "#c9f7ff"
INK = "#0c1018"           # universal sprite outline (blue-black instead of pure black)
WHITE = "#f4fbff"

# HUD panels
PANEL = "#0d1320"
PANEL_EDGE = "#3a4968"
PANEL_ALPHA = 0xA6        # ~65 % opaque

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
    "netherite": Ramp("#322b38", "#584e63", "#8c7f99", "#c6b0cc"),
}

# Guard / head-socket colours for each material (a darker, more neutral trim)
TRIM: dict[str, Ramp] = {
    "wooden":    Ramp("#4f3216", "#6b4521", "#86592b", "#a0713c"),
    "stone":     Ramp("#434950", "#5f666d", "#7c848b", "#98a0a7"),
    "copper":    Ramp("#7d3414", "#a9501f", "#cc6c33", "#e88a52"),
    "iron":      Ramp("#68737c", "#8c98a2", "#aeb9c2", "#cfd8df"),
    "golden":    Ramp("#a86e06", "#d9960f", "#f2b928", "#ffd75e"),
    "diamond":   Ramp("#0e7886", "#169aa8", "#27bfc4", "#6bdcd9"),
    "netherite": Ramp("#1b161f", "#2f2837", "#463d50", "#5f5469"),
}

HANDLE = Ramp("#583717", "#7d5226", "#a47036", "#c18d4e")   # classic stick

MATERIAL_ORDER = ["wooden", "stone", "copper", "iron", "golden", "diamond", "netherite"]

# ------------------------------------------------------------------ misc palettes
RED = Ramp("#a3142b", "#e4283f", "#ff6478", "#ffc1c9")
GOLD = MATERIALS["golden"]
GREEN = Ramp("#2c8a2a", "#52cc3b", "#97ee6a", "#d6ffb8")
ORANGE = Ramp("#b5531b", "#f0832a", "#ffb04f", "#ffe0a8")
PURPLE = Ramp("#4a1f86", "#8a46dd", "#bc83ff", "#e9d4ff")
STEEL = Ramp("#46505c", "#6f7c8a", "#9aa8b6", "#c9d4de")
