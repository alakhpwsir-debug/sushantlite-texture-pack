"""Item-model tweaks: a lower shield and a smaller totem pop; everything else is vanilla size.

Only the ``display`` transforms are changed; geometry, textures and item
definitions stay vanilla, so these files are safe across item additions.

Swords, tools, food, potions, bows and the mace are drawn at their **vanilla** first-person size
(the look this pack follows has full-size swords).  A model whose scale equals the vanilla value is
not written at all, so the game's own file is used.  Lower a value in ``SCALES`` to get small
items back (0.50 for tools and generated items was the 0.1/0.2 look) and re-run ``generate.py``.

How the sizes work
------------------
Minecraft applies a display transform as translate -> rotate -> scale around
the model centre.  Lowering ``scale`` therefore shrinks the item *around the
same point on screen* without moving it, which is why only scales (never
translations) are changed here.

All base values below are the vanilla numbers (identical on 1.21.11, 26.1.x,
26.2 and 26.3, verified against the reference snapshots, except the shield's
y-translation, which differs between 1.21.11 and 26.1+ and therefore ships in
an overlay); the SushantLite scale is applied on top.  Tune the constants in
``SCALES`` to taste.
"""
from __future__ import annotations

# --------------------------------------------------------------------------- #
# Tunables (vanilla value in the comment)
# --------------------------------------------------------------------------- #
VANILLA = {
    "handheld": 0.68,       # swords, axes, pickaxes, ... in first person
    "generated": 0.68,      # food, pearls, potions, totems, ... in first person
    "bow": 0.68,            # bow + crossbow in first person
    "mace": 0.90,
    "spear": 1.00,          # multiplier on the vanilla x/y scale (1.36); z stays vanilla
    "shield": 1.25,
    "totem_pop": 1.00,
}

SCALES = {
    "handheld": 0.68,       # vanilla size
    "generated": 0.68,      # vanilla size
    "bow": 0.68,            # vanilla size
    "mace": 0.90,           # vanilla size
    "spear": 1.00,          # vanilla size
    "shield": 0.90,         # lower shield, idle and blocking               (vanilla 1.25)
    "totem_pop": 0.50,      # totem-of-undying activation animation         (vanilla 1.00)
}


def changed(key: str) -> bool:
    """True when the SushantLite value differs from vanilla, i.e. the model file has to ship."""
    return abs(SCALES[key] - VANILLA[key]) > 1e-9

NS = "assets/minecraft/models/item"


def _t(rotation, translation, scale) -> dict:
    s = scale if isinstance(scale, (list, tuple)) else [scale] * 3
    return {"rotation": list(rotation), "translation": list(translation), "scale": list(s)}


def _handheld() -> dict:
    k = SCALES["handheld"]
    return {
        "parent": "item/generated",
        "display": {
            "thirdperson_righthand": _t([0, -90, 55], [0, 4.0, 0.5], 0.85),
            "thirdperson_lefthand": _t([0, 90, -55], [0, 4.0, 0.5], 0.85),
            "firstperson_righthand": _t([0, -90, 25], [1.13, 3.2, 1.13], k),
            "firstperson_lefthand": _t([0, 90, -25], [1.13, 3.2, 1.13], k),
        },
    }


def _generated() -> dict:
    k = SCALES["generated"]
    return {
        "parent": "builtin/generated",
        "gui_light": "front",
        "display": {
            "ground": _t([0, 0, 0], [0, 2, 0], 0.5),
            "head": _t([0, 180, 0], [0, 13, 7], 1),
            "thirdperson_righthand": _t([0, 0, 0], [0, 3, 1], 0.55),
            "firstperson_righthand": _t([0, -90, 25], [1.13, 3.2, 1.13], k),
            "fixed": {"rotation": [0, 180, 0], "scale": [1, 1, 1]},
        },
    }


def _bow() -> dict:
    k = SCALES["bow"]
    return {
        "parent": "item/generated",
        "textures": {"layer0": "item/bow"},
        "display": {
            "thirdperson_righthand": _t([-80, 260, -40], [-1, -2, 2.5], 0.9),
            "thirdperson_lefthand": _t([-80, -280, 40], [-1, -2, 2.5], 0.9),
            "firstperson_righthand": _t([0, -90, 25], [1.13, 3.2, 1.13], k),
            "firstperson_lefthand": _t([0, 90, -25], [1.13, 3.2, 1.13], k),
        },
    }


def _crossbow() -> dict:
    k = SCALES["bow"]
    return {
        "parent": "item/generated",
        "textures": {"layer0": "item/crossbow_standby"},
        "display": {
            "thirdperson_righthand": _t([-90, 0, -60], [2, 0.1, -3], 0.9),
            "thirdperson_lefthand": _t([-90, 0, 30], [2, 0.1, -3], 0.9),
            "firstperson_righthand": _t([-90, 0, -55], [1.13, 3.2, 1.13], k),
            "firstperson_lefthand": _t([-90, 0, 35], [1.13, 3.2, 1.13], k),
        },
    }


def _handheld_mace() -> dict:
    k = SCALES["mace"]
    return {
        "parent": "item/handheld",
        "display": {
            "thirdperson_righthand": _t([0, -90, 55], [0, 4.0, 1], 1),
            "thirdperson_lefthand": _t([0, 90, -55], [0, 4.0, 1], 1),
            "firstperson_righthand": _t([0, -90, 25], [0, 3, 0.8], k),
            "firstperson_lefthand": _t([0, 90, -25], [0, 3, 0.8], k),
        },
    }


def _spear_in_hand() -> dict:
    k = SCALES["spear"]
    fp = [round(1.36 * k, 3), round(1.36 * k, 3), 0.68]
    return {
        "gui_light": "front",
        "parent": "item/generated",
        "display": {
            "firstperson_righthand": _t([-20, 90, -35], [3.13, 2.0, 0.13], fp),
            "firstperson_lefthand": _t([-20, -90, 35], [3.13, 2.0, 0.13], fp),
            "thirdperson_righthand": _t([5, 270, -40], [0, 2, 2], [1.7, 1.7, 0.85]),
            "thirdperson_lefthand": _t([5, -270, 40], [0, 2, 2], [1.7, 1.7, 0.85]),
        },
    }


# first-person y-translation of the shield: vanilla changed these in 26.1 to compensate for the flip that
# the shield item definition gained, so each version needs its own number to keep the same pose
SHIELD_Y = {"idle": {"26.1+": 1.75, "1.21.11": 2.0}, "blocking": {"26.1+": 3.25, "1.21.11": 5.0}}


def _shield(version: str = "26.1+") -> dict:
    k = SCALES["shield"]
    y = SHIELD_Y["idle"][version]
    return {
        "gui_light": "front",
        "textures": {"particle": "block/dark_oak_planks"},
        "display": {
            "thirdperson_righthand": _t([0, 90, 0], [10, 6, -4], 1),
            "thirdperson_lefthand": _t([0, 90, 0], [10, 6, 12], 1),
            "firstperson_righthand": _t([0, 180, 5], [-10, y, -10], k),
            "firstperson_lefthand": _t([0, 180, 5], [10, 0, -10], k),
            "gui": _t([15, -25, -5], [2, 3, 0], 0.65),
            "fixed": _t([0, 180, 0], [-4.5, 4.5, -5], 0.55),
            "on_shelf": _t([0, 0, 0], [11, 18.5, 8.7], 1.4),
            "ground": _t([0, 0, 0], [2, 4, 2], 0.25),
        },
    }


def _shield_blocking(version: str = "26.1+") -> dict:
    k = SCALES["shield"]
    y = SHIELD_Y["blocking"][version]
    return {
        "gui_light": "front",
        "textures": {"particle": "block/dark_oak_planks"},
        "display": {
            "thirdperson_righthand": _t([45, 155, 0], [-3.49, 11, -2], 1),
            "thirdperson_lefthand": _t([45, 155, 0], [11.51, 7, 2.5], 1),
            "firstperson_righthand": _t([0, 180, -5], [-15, y, -11], k),
            "firstperson_lefthand": _t([0, 180, -5], [5, 5, -11], k),
            "gui": _t([15, -25, -5], [2, 3, 0], 0.65),
        },
    }


def _totem() -> dict:
    """Small totem: the activation 'pop' is rendered in the FIXED display context."""
    return {
        "parent": "minecraft:item/generated",
        "textures": {"layer0": "minecraft:item/totem_of_undying"},
        "display": {
            "fixed": {"rotation": [0, 180, 0], "scale": [SCALES["totem_pop"]] * 3},
        },
    }


def _enchanted_apple() -> dict:
    """Vanilla reuses the golden-apple sprite (glint only); SushantLite gives it its own look."""
    return {
        "parent": "minecraft:item/generated",
        "textures": {"layer0": "minecraft:item/enchanted_golden_apple"},
    }


def generate(pack) -> None:
    pack.json(f"{NS}/enchanted_golden_apple.json", _enchanted_apple())
    if changed("handheld"):
        pack.json(f"{NS}/handheld.json", _handheld())
    if changed("generated"):
        pack.json(f"{NS}/generated.json", _generated())
    if changed("bow"):
        pack.json(f"{NS}/bow.json", _bow())
        pack.json(f"{NS}/crossbow.json", _crossbow())
    if changed("mace"):
        pack.json(f"{NS}/handheld_mace.json", _handheld_mace())
    if changed("spear"):
        pack.json(f"{NS}/spear_in_hand.json", _spear_in_hand())
    pack.json(f"{NS}/shield.json", _shield("26.1+"))                          # base: 26.1+ numbers
    pack.json(f"{NS}/shield_blocking.json", _shield_blocking("26.1+"))
    pack.json(f"{NS}/shield.json", _shield("1.21.11"), overlay="overlay_1_21_11")       # exact 1.21.11 pose
    pack.json(f"{NS}/shield_blocking.json", _shield_blocking("1.21.11"), overlay="overlay_1_21_11")
    pack.json(f"{NS}/totem_of_undying.json", _totem())
