"""pack.mcmeta -- the pack's identity and supported-version range."""
from __future__ import annotations

from .. import config


def _description() -> list[dict]:
    # A JSON array is "first component + children"; children inherit its style,
    # so every follow-up component resets bold explicitly.
    return [
        {"text": config.PACK_NAME, "color": "aqua", "bold": True},
        {"text": f" - {config.PACK_TAGLINE}\n", "color": "gray", "bold": False},
        {"text": "1.21.11 to 26.3 | low fire, clean HUD", "color": "dark_gray", "bold": False},
    ]


def generate(pack) -> None:
    mcmeta: dict = {
        "pack": {
            "description": _description(),
            # Since 1.21.9 (25w31a) these replace pack_format / supported_formats.  They must
            # be the *only* format fields because the pack does not support anything older.
            "min_format": config.MIN_FORMAT,
            "max_format": config.MAX_FORMAT,
        }
    }
    entries = [
        {"directory": name, "min_format": lo, "max_format": hi}
        for name, (lo, hi) in config.OVERLAYS.items()
        if name in pack.used_overlays()
    ]
    if entries:
        mcmeta["overlays"] = {"entries": entries}
    pack.json("pack.mcmeta", mcmeta)
