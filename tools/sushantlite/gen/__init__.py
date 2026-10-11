"""Generator registry.  Order matters only for ``meta`` (it must run last)."""
from . import effects, hud, icon, items, meta, models, shield, sky, sounds

GENERATORS = [
    ("effects", effects.generate),
    ("hud", hud.generate),
    ("items", items.generate),
    ("shield", shield.generate),
    ("sky", sky.generate),
    ("models", models.generate),
    ("sounds", sounds.generate),
    ("icon", icon.generate),
    ("meta", meta.generate),     # keep last: it lists the overlays the other generators used
]
