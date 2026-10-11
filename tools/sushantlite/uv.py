"""Texture-space helpers shared by the entity generators (armour, shield, projectiles ...).

Minecraft unwraps every cuboid ("box") of an entity model into a fixed cross-shaped patch of
the texture.  For a box of size ``w x h x d`` at ``texOffs(u, v)``::

            d    w    w
          +----+----+----+
        d | .  | top|bott|        top    = (u + d,         v,     w, d)
          +----+----+----+----+   bottom = (u + d + w,     v,     w, d)
        h |west|front|east|back|   west   = (u,             v + d, d, h)
          +----+----+----+----+   front  = (u + d,         v + d, w, h)
            d    w    d    w      east   = (u + d + w,     v + d, d, h)
                                   back   = (u + d + w + d, v + d, w, h)

``scale`` is the texture density relative to the model's declared texture size (the 1.21+ end
crystal ships a 128x64 PNG for a 64x32 model, so every number doubles).
"""
from __future__ import annotations

from typing import Callable

from .sprite import Sprite

Rect = tuple[int, int, int, int]       # x, y, width, height (pixels)


def box_faces(u: int, v: int, w: int, h: int, d: int, scale: int = 1) -> dict[str, Rect]:
    """Cube UV unwrap: face name -> (x, y, width, height) in pixels."""
    faces = {
        "top": (u + d, v, w, d),
        "bottom": (u + d + w, v, w, d),
        "west": (u, v + d, d, h),
        "front": (u + d, v + d, w, h),
        "east": (u + d + w, v + d, d, h),
        "back": (u + d + w + d, v + d, w, h),
    }
    return {name: tuple(c * scale for c in rect) for name, rect in faces.items()}  # type: ignore[misc]


def rect_cells(rect: Rect, keep: Callable[[int, int], bool] | None = None) -> set[tuple[int, int]]:
    """All (x, y) pixels of ``rect`` (optionally only those where ``keep(local_x, local_y)``)."""
    x, y, w, h = rect
    return {(x + lx, y + ly) for ly in range(h) for lx in range(w) if keep is None or keep(lx, ly)}


def sub_rows(rect: Rect, first: int, last: int) -> Rect:
    """The part of ``rect`` covering *texture* rows ``first..last`` (inclusive)."""
    x, y, w, h = rect
    top = max(y, first)
    bottom = min(y + h - 1, last)
    return (x, top, w, max(0, bottom - top + 1))


def paint(s: Sprite, rect: Rect, fn) -> None:
    """Fill ``rect`` with ``fn(local_x, local_y)`` (``None`` leaves the pixel untouched)."""
    x, y, w, h = rect
    for ly in range(h):
        for lx in range(w):
            c = fn(lx, ly)
            if c is not None:
                s.set(x + lx, y + ly, c)
