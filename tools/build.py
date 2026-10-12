#!/usr/bin/env python3
"""Build installable resource pack zips into dist/.

    python tools/build.py                  # SushantLite-vX.Y.Z.zip + ...-static.zip
    python tools/build.py --no-static      # only the animated pack
    python tools/build.py --version 0.2.0  # override the version used in file names

The zips are reproducible: files are added in sorted order with fixed timestamps,
so identical sources always give a byte-identical archive (nice for release checksums).

Variants
    SushantLite-vX.zip         animated fire + water (default)
    SushantLite-vX-static.zip  fire and water frozen to one frame: fewer texture updates
                               for very low-end machines
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402

import validate  # noqa: E402
from sushantlite import config  # noqa: E402

# animated textures the static variant freezes (first frame, square)
ANIMATED = [
    "assets/minecraft/textures/block/fire_0.png",
    "assets/minecraft/textures/block/fire_1.png",
    "assets/minecraft/textures/block/water_still.png",
    "assets/minecraft/textures/block/water_flow.png",
]
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def make_static(staging: Path) -> None:
    for rel in ANIMATED:
        png = staging / rel
        if not png.exists():
            continue
        with Image.open(png) as im:
            frame = im.convert("RGBA").crop((0, 0, im.width, im.width))
        frame.save(png, format="PNG", optimize=True)
        meta = Path(str(png) + ".mcmeta")
        if meta.exists():
            meta.unlink()
    mc = staging / "pack.mcmeta"
    data = json.loads(mc.read_text(encoding="utf-8"))
    desc = data["pack"]["description"]
    if isinstance(desc, list) and len(desc) > 1:
        desc[1]["text"] = f" - {config.PACK_TAGLINE} (static)\n"
    mc.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_zip(src: Path, dest: Path) -> str:
    files = sorted((p for p in src.rglob("*") if p.is_file()), key=lambda p: (p.name != "pack.mcmeta", p.relative_to(src).as_posix()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in files:
            info = zipfile.ZipInfo(p.relative_to(src).as_posix(), FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            zf.writestr(info, p.read_bytes(), compresslevel=9)
    return hashlib.sha256(dest.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default=config.PACK_VERSION)
    ap.add_argument("--no-static", action="store_true", help="skip the static variant")
    ap.add_argument("--no-validate", action="store_true", help="skip validation (not recommended)")
    ap.add_argument("--out", type=Path, default=config.DIST_DIR)
    args = ap.parse_args()

    if not config.PACK_DIR.is_dir():
        print(f"{config.PACK_DIR} does not exist; run `python tools/generate.py` first", file=sys.stderr)
        return 2
    if not args.no_validate:
        if validate.run(config.PACK_DIR, quiet=True) != 0:
            print("validation failed -- run `python tools/validate.py` for details", file=sys.stderr)
            return 1

    version = args.version.lstrip("v")
    results = []
    main_zip = args.out / f"{config.PACK_NAME}-v{version}.zip"
    results.append((main_zip, write_zip(config.PACK_DIR, main_zip)))

    if not args.no_static:
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / config.PACK_NAME
            shutil.copytree(config.PACK_DIR, staging)
            make_static(staging)
            if not args.no_validate and validate.run(staging, quiet=True) != 0:
                print("static variant failed validation", file=sys.stderr)
                return 1
            static_zip = args.out / f"{config.PACK_NAME}-v{version}-static.zip"
            results.append((static_zip, write_zip(staging, static_zip)))

    for path, digest in results:
        print(f"{path.relative_to(config.ROOT)}  {path.stat().st_size / 1024:.0f} KiB  sha256 {digest[:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
