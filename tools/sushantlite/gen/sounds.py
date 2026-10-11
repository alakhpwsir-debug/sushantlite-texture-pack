"""Audio tweaks (no audio files are shipped, only sound-event overrides).

* "No cave sounds"  -> the ambient.cave event is emptied.
* "Quiet explosions" -> entity.generic.explode keeps its vanilla samples but plays at ~35 % volume.

A resource pack's sounds.json is merged per *event*, so listing just these
two events leaves every other sound untouched.  The sample names below were
verified to be identical on 1.21.11, 26.1.2, 26.2 and 26.3.
"""
from __future__ import annotations

EXPLOSION_VOLUME = 0.35


def generate(pack) -> None:
    sounds = {
        "ambient.cave": {"replace": True, "sounds": []},
        "entity.generic.explode": {
            "replace": True,
            "sounds": [{"name": f"random/explode{i}", "volume": EXPLOSION_VOLUME} for i in range(1, 5)],
            "subtitle": "subtitles.entity.generic.explode",
        },
    }
    pack.json("assets/minecraft/sounds.json", sounds)
