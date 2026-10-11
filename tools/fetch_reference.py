#!/usr/bin/env python3
"""Build the compact vanilla-asset index used by tools/validate.py.

The index lists, per Minecraft version, every path a resource pack can
override (textures, item models, item definitions, particles, equipment,
atlases, sound events) together with PNG sizes.  It contains *names and sizes
only* -- no Mojang artwork -- and is committed to the repo so CI can validate
the pack without downloading ~800 MB of assets per version.

Usage:
    python tools/fetch_reference.py                       # re-index the versions already in the index
    python tools/fetch_reference.py 26.4 --add            # add a new version to the index
    python tools/fetch_reference.py --cache-dir /tmp/ref  # reuse existing clones

Snapshots come from https://github.com/misode/mcmeta (tag "<version>-assets").
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sushantlite import config  # noqa: E402

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install -r requirements.txt")

INDEXED_PREFIXES = ("textures/", "models/item/", "items/", "particles/", "equipment/", "atlases/")
INDEX_FILE = config.REFERENCE_DIR / "vanilla-index.tsv.gz"
VERSIONS_FILE = config.REFERENCE_DIR / "versions.json"


def clone(version: str, cache_dir: Path) -> Path:
    target = cache_dir / version
    if (target / "assets" / "minecraft").is_dir():
        return target
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"  cloning {version} (shallow) ...", flush=True)
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    subprocess.run(
        ["git", "clone", "--quiet", "--depth", "1", "--single-branch",
         "--branch", f"{version}-assets", config.MCMETA_REPO, str(target)],
        check=True, env=env,
    )
    return target


def scan(version_dir: Path) -> tuple[dict[str, str], list[str], dict]:
    """Return ({relative path: size-or-'-'}, [sound events], version.json)."""
    root = version_dir / "assets" / "minecraft"
    files: dict[str, str] = {}
    for dirpath, _dirs, names in os.walk(root):
        for name in names:
            full = Path(dirpath) / name
            rel = full.relative_to(root).as_posix()
            if not rel.startswith(INDEXED_PREFIXES):
                continue
            if rel.endswith(".png"):
                with Image.open(full) as im:
                    files[rel] = f"{im.width}x{im.height}"
            else:
                files[rel] = "-"
    sounds = json.loads((root / "sounds.json").read_text(encoding="utf-8"))
    info = json.loads((version_dir / "version.json").read_text(encoding="utf-8"))
    return files, sorted(sounds), info


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("versions", nargs="*", help="versions to index (default: config.REFERENCE_VERSIONS)")
    ap.add_argument("--add", action="store_true", help="add the given versions to the existing list instead of replacing it")
    ap.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache" / "sushantlite" / "mcmeta",
                    help="where shallow clones of misode/mcmeta are kept")
    args = ap.parse_args()

    # base list: whatever the committed index currently covers (config.REFERENCE_VERSIONS seeds a fresh checkout)
    if VERSIONS_FILE.exists():
        versions = [v["id"] for v in json.loads(VERSIONS_FILE.read_text(encoding="utf-8"))["versions"]]
    else:
        versions = list(config.REFERENCE_VERSIONS)
    if args.versions:
        versions = (versions + args.versions) if args.add else args.versions
    versions = list(dict.fromkeys(versions))

    per_version: list[dict[str, str]] = []
    events: list[list[str]] = []
    meta = []
    for v in versions:
        print(f"[{v}]", flush=True)
        d = clone(v, args.cache_dir)
        files, sound_events, info = scan(d)
        per_version.append(files)
        events.append(sound_events)
        meta.append({
            "id": v,
            "resource_pack_format": [info["resource_pack_version"], info.get("resource_pack_version_minor", 0)],
            "released": info.get("release_time", "")[:10],
        })
        print(f"  {len(files)} indexed files, {len(sound_events)} sound events, "
              f"resource pack format {meta[-1]['resource_pack_format']}")

    lines = ["#versions\t" + "\t".join(versions)]
    all_paths = sorted(set().union(*[set(f) for f in per_version]))
    for p in all_paths:
        sizes = [f.get(p) for f in per_version]
        mask = "".join("1" if s is not None else "0" for s in sizes)
        present = [s for s in sizes if s is not None]
        size = present[0] if len(set(present)) == 1 else ",".join(s or "x" for s in sizes)
        lines.append(f"{mask}\t{size}\t{p}")
    all_events = sorted(set().union(*[set(e) for e in events]))
    for e in all_events:
        mask = "".join("1" if e in ev else "0" for ev in events)
        lines.append(f"{mask}\t-\tsound-event:{e}")

    config.REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    # mtime=0 keeps the gzip byte-for-byte reproducible
    with open(INDEX_FILE, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as gz:
        gz.write(("\n".join(lines) + "\n").encode("utf-8"))
    VERSIONS_FILE.write_text(json.dumps({"versions": meta}, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {INDEX_FILE.relative_to(config.ROOT)} ({INDEX_FILE.stat().st_size // 1024} KiB, "
          f"{len(lines) - 1} entries) and {VERSIONS_FILE.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
