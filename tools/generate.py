#!/usr/bin/env python3
"""Regenerate the SushantLite resource pack (SushantLite/) from code.

    python tools/generate.py                 # regenerate everything
    python tools/generate.py --only hud items
    python tools/generate.py --list
    python tools/generate.py --profile full  # every texture the generators can draw (default: barebones)

Files the generator produced earlier but no longer produces are deleted, except
paths listed in tools/locked.txt (use that to protect hand-edited art).
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sushantlite import config, gen  # noqa: E402
from sushantlite.out import PackWriter  # noqa: E402


def same_png(a: Path, b: Path, tolerance: int = 2) -> bool:
    """Pixel-wise comparison.  PNG bytes depend on the zlib build, and floating-point maths may round a
    value differently on another platform's libm, so allow +-``tolerance`` per channel (real edits
    differ by far more)."""
    with Image.open(a) as ia, Image.open(b) as ib:
        ia, ib = ia.convert("RGBA"), ib.convert("RGBA")
        if ia.size != ib.size:
            return False
        extrema = ImageChops.difference(ia, ib).getextrema()
        return all(hi <= tolerance for _lo, hi in extrema)


def check() -> int:
    """Regenerate into a temp dir and compare with SushantLite/ (exit 1 on any difference)."""
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / config.PACK_NAME
        pack = PackWriter(fresh)
        for _name, fn in gen.GENERATORS:
            fn(pack)
        locked = pack.locked
        expected = set(pack.written) - locked
        actual = {p.relative_to(config.PACK_DIR).as_posix() for p in config.PACK_DIR.rglob("*") if p.is_file()} - locked
        problems = []
        problems += [f"missing from pack: {r}" for r in sorted(expected - actual)]
        problems += [f"not produced by the generator: {r}" for r in sorted(actual - expected)]
        for rel in sorted(expected & actual):
            a, b = config.PACK_DIR / rel, fresh / rel
            same = same_png(a, b) if rel.endswith(".png") else a.read_bytes() == b.read_bytes()
            if not same:
                problems.append(f"differs: {rel}")
    if problems:
        print("\n".join(problems[:50]))
        print(f"\n{len(problems)} difference(s): run `python tools/generate.py` and commit the result")
        return 1
    print(f"{config.PACK_DIR.name}/ is up to date with the generators ({len(expected)} files)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", metavar="NAME", help="run only these generators")
    ap.add_argument("--list", action="store_true", help="list generators and exit")
    ap.add_argument("--check", action="store_true", help="verify the committed pack matches the generators (for CI)")
    ap.add_argument("--profile", choices=("barebones", "full"), help="scope of the pack (default: barebones; see config.py)")
    args = ap.parse_args()
    if args.profile:
        config.PROFILE = args.profile
    if args.check:
        return check()

    names = [n for n, _ in gen.GENERATORS]
    if args.list:
        print("\n".join(names))
        return 0
    if args.only:
        unknown = set(args.only) - set(names)
        if unknown:
            ap.error(f"unknown generator(s): {', '.join(sorted(unknown))} (available: {', '.join(names)})")

    pack = PackWriter(partial=bool(args.only))
    t0 = time.time()
    for name, fn in gen.GENERATORS:
        if args.only and name not in args.only and name != "meta":
            continue
        before = len(pack.written)
        fn(pack)
        print(f"  {name:<8} {len(pack.written) - before:>4} files")
    written, removed = pack.finalize(partial=bool(args.only))
    print(f"\n{written} files in {config.PACK_DIR.name}/ ({removed} stale removed) in {time.time() - t0:.1f}s")
    if pack.skipped_locked:
        print(f"{len(pack.skipped_locked)} locked file(s) left untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
