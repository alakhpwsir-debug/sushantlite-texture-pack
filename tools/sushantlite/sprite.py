"""A tiny pixel-art toolkit on top of Pillow.

A ``Sprite`` is a grid of RGBA pixels (``None`` = fully transparent).  It has
just enough drawing primitives to author clean 16x16 art in code: lines,
rectangles, discs, ASCII-art templates with palettes, automatic outlines,
mirroring, shifting and alpha compositing.
"""
from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from PIL import Image

RGBA = tuple[int, int, int, int]
ColorLike = "str | tuple[int, ...] | None"


def rgba(c) -> RGBA | None:
    """Accept '#rgb', '#rrggbb', '#rrggbbaa', (r,g,b), (r,g,b,a) or None."""
    if c is None:
        return None
    if isinstance(c, str):
        s = c.lstrip("#")
        if len(s) == 3:
            s = "".join(ch * 2 for ch in s)
        if len(s) == 6:
            s += "ff"
        if len(s) != 8:
            raise ValueError(f"bad colour {c!r}")
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16))
    if len(c) == 3:
        return (int(c[0]), int(c[1]), int(c[2]), 255)
    return (int(c[0]), int(c[1]), int(c[2]), int(c[3]))


def mix(a, b, t: float) -> RGBA:
    """Linear blend of two colours (t=0 -> a, t=1 -> b)."""
    a, b = rgba(a), rgba(b)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(4))  # type: ignore[return-value]


def with_alpha(c, alpha: int) -> RGBA:
    r, g, b, _ = rgba(c)
    return (r, g, b, max(0, min(255, int(alpha))))


def over(dst: RGBA | None, src: RGBA | None) -> RGBA | None:
    """Porter-Duff 'src over dst'."""
    if src is None or src[3] == 0:
        return dst
    if dst is None or dst[3] == 0 or src[3] == 255:
        return src
    sa, da = src[3] / 255.0, dst[3] / 255.0
    oa = sa + da * (1 - sa)
    if oa <= 0:
        return None
    out = [round((src[i] * sa + dst[i] * da * (1 - sa)) / oa) for i in range(3)]
    return (out[0], out[1], out[2], round(oa * 255))


class Sprite:
    def __init__(self, w: int = 16, h: int = 16):
        self.w, self.h = w, h
        self.px: list[list[RGBA | None]] = [[None] * w for _ in range(h)]

    # ------------------------------------------------------------------ basics
    def copy(self) -> "Sprite":
        s = Sprite(self.w, self.h)
        s.px = [row[:] for row in self.px]
        return s

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def set(self, x: int, y: int, c) -> "Sprite":
        if self.inside(x, y):
            self.px[y][x] = rgba(c)
        return self

    def get(self, x: int, y: int) -> RGBA | None:
        return self.px[y][x] if self.inside(x, y) else None

    def solid(self, x: int, y: int) -> bool:
        p = self.get(x, y)
        return p is not None and p[3] > 0

    def mask(self) -> set[tuple[int, int]]:
        return {(x, y) for y in range(self.h) for x in range(self.w) if self.solid(x, y)}

    def fill(self, c) -> "Sprite":
        c = rgba(c)
        self.px = [[c] * self.w for _ in range(self.h)]
        return self

    # --------------------------------------------------------------- primitives
    def rect(self, x: int, y: int, w: int, h: int, c) -> "Sprite":
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)
        return self

    def frame(self, x: int, y: int, w: int, h: int, c) -> "Sprite":
        """1px rectangle outline."""
        self.rect(x, y, w, 1, c).rect(x, y + h - 1, w, 1, c)
        self.rect(x, y, 1, h, c).rect(x + w - 1, y, 1, h, c)
        return self

    def line(self, x0: int, y0: int, x1: int, y1: int, c) -> "Sprite":
        """Bresenham line (inclusive of both end points)."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        return self

    def disc(self, cx: float, cy: float, r: float, c) -> "Sprite":
        for y in range(self.h):
            for x in range(self.w):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    self.set(x, y, c)
        return self

    def points(self, pts: Iterable[tuple[int, int]], c) -> "Sprite":
        for x, y in pts:
            self.set(x, y, c)
        return self

    # --------------------------------------------------------------- composing
    def blit(self, other: "Sprite", x: int = 0, y: int = 0, blend: bool = False) -> "Sprite":
        for yy in range(other.h):
            for xx in range(other.w):
                p = other.px[yy][xx]
                if p is None:
                    continue
                if blend:
                    self.set(x + xx, y + yy, over(self.get(x + xx, y + yy), p))
                else:
                    self.set(x + xx, y + yy, p)
        return self

    def shifted(self, dx: int, dy: int) -> "Sprite":
        s = Sprite(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] is not None:
                    s.set(x + dx, y + dy, self.px[y][x])
        return s

    def flip_h(self) -> "Sprite":
        s = Sprite(self.w, self.h)
        s.px = [row[::-1] for row in self.px]
        return s

    def flip_v(self) -> "Sprite":
        s = Sprite(self.w, self.h)
        s.px = [row[:] for row in self.px[::-1]]
        return s

    def outline(self, c, diagonals: bool = True) -> "Sprite":
        """Surround every opaque pixel with colour ``c`` (only on transparent cells)."""
        c = rgba(c)
        todo = []
        nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonals:
            nbrs += [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        for y in range(self.h):
            for x in range(self.w):
                if self.solid(x, y):
                    continue
                if any(self.solid(x + dx, y + dy) for dx, dy in nbrs):
                    todo.append((x, y))
        for x, y in todo:
            self.px[y][x] = c
        return self

    def recolor(self, mapping: Mapping) -> "Sprite":
        m = {rgba(k): rgba(v) for k, v in mapping.items()}
        for y in range(self.h):
            for x in range(self.w):
                p = self.px[y][x]
                if p in m:
                    self.px[y][x] = m[p]
        return self

    # ------------------------------------------------------------- construction
    @classmethod
    def from_ascii(cls, rows: Sequence[str], legend: Mapping[str, object]) -> "Sprite":
        """Build a sprite from ASCII art; '.' and ' ' are transparent.

        Every other character must be present in ``legend`` (char -> colour).
        """
        h = len(rows)
        w = max(len(r) for r in rows)
        s = cls(w, h)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch in ". ":
                    continue
                if ch not in legend:
                    raise KeyError(f"ascii sprite uses {ch!r} (row {y}, col {x}) but legend has no entry")
                s.px[y][x] = rgba(legend[ch])
        return s

    # ------------------------------------------------------------------ output
    def to_image(self, scale: int = 1) -> Image.Image:
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        put = img.putpixel
        for y in range(self.h):
            for x in range(self.w):
                p = self.px[y][x]
                if p is not None:
                    put((x, y), p)
        if scale != 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return img


def stack_frames(frames: Sequence[Sprite]) -> Image.Image:
    """Stack equally-wide frames vertically (Minecraft animation strip)."""
    w = frames[0].w
    h = sum(f.h for f in frames)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for f in frames:
        assert f.w == w, "all animation frames must have the same width"
        out.paste(f.to_image(), (0, y))
        y += f.h
    return out


def blank(w: int, h: int) -> Image.Image:
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))
