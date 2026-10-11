"""Seamlessly tiling value noise (pure Python, deterministic)."""
from __future__ import annotations

import random


def _smooth(t: float) -> float:
    return t * t * (3 - 2 * t)


def periodic_noise(size: int, cells: int, seed: int) -> list[list[float]]:
    """size x size noise in [0, 1) that tiles perfectly (random lattice of cells x cells, wrapped)."""
    rng = random.Random(seed)
    lattice = [[rng.random() for _ in range(cells)] for _ in range(cells)]
    step = size / cells
    out = [[0.0] * size for _ in range(size)]
    for y in range(size):
        gy = y / step
        y0 = int(gy) % cells
        y1 = (y0 + 1) % cells
        ty = _smooth(gy - int(gy))
        for x in range(size):
            gx = x / step
            x0 = int(gx) % cells
            x1 = (x0 + 1) % cells
            tx = _smooth(gx - int(gx))
            a = lattice[y0][x0] + (lattice[y0][x1] - lattice[y0][x0]) * tx
            b = lattice[y1][x0] + (lattice[y1][x1] - lattice[y1][x0]) * tx
            out[y][x] = a + (b - a) * ty
    return out


def fractal(size: int, octaves: list[tuple[int, float]], seed: int) -> list[list[float]]:
    """Weighted sum of tiling noise octaves [(cells, weight), ...]; normalised to 0..1."""
    total = sum(w for _, w in octaves)
    acc = [[0.0] * size for _ in range(size)]
    for i, (cells, w) in enumerate(octaves):
        n = periodic_noise(size, cells, seed * 31 + i * 7919)
        for y in range(size):
            row, nrow = acc[y], n[y]
            for x in range(size):
                row[x] += nrow[x] * w / total
    return acc


def quantile(field: list[list[float]], q: float) -> float:
    flat = sorted(v for row in field for v in row)
    return flat[min(len(flat) - 1, int(q * len(flat)))]
