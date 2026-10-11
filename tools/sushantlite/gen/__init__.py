"""Generator registry.  Order matters only for ``meta`` (it must run last)."""
from . import armor, effects, entities, food, hud, icon, items, meta, models, ranged, shield, sky, sounds, wings

GENERATORS = [
    ("effects", effects.generate),
    ("hud", hud.generate),
    ("items", items.generate),
    ("food", food.generate),
    ("ranged", ranged.generate),
    ("shield", shield.generate),
    ("armor", armor.generate),
    ("wings", wings.generate),
    ("entities", entities.generate),
    ("sky", sky.generate),
    ("models", models.generate),
    ("sounds", sounds.generate),
    ("icon", icon.generate),
    ("meta", meta.generate),     # keep last: it lists the overlays the other generators used
]
