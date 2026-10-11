#!/usr/bin/env python3
"""Validate the SushantLite pack against every supported Minecraft version.

I cannot launch Minecraft in CI, so this is the next best thing: for each
reference version (1.21.11, 26.1.2, 26.2, 26.3) it builds the *effective* file
set (base + the overlays active on that version) and checks, per file:

  * the path is a real vanilla path (or is referenced by one of our own JSON files)
  * PNG dimensions match vanilla (animation strips: same width, whole frames)
  * .mcmeta files are valid and sit next to their PNG
  * item models: parents and textures resolve, display transforms are sane
  * particle definitions, sound events, file naming rules, pack.mcmeta / overlays

    python tools/validate.py            # exit status 1 on errors
    python tools/validate.py -v         # also list informational notes
    python tools/validate.py --strict   # warnings fail too
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sushantlite import config  # noqa: E402
from sushantlite.reference import Reference  # noqa: E402

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install -r requirements.txt")

NAME_RE = re.compile(r"^[a-z0-9/._-]+$")
OVERLAY_DIR_RE = re.compile(r"^[a-z0-9_.-]+$")
JUNK = {".DS_Store", "Thumbs.db", "desktop.ini"}
ROOT_FILES = {"pack.mcmeta", "pack.png"}
Version = tuple[int, int]


class Report:
    def __init__(self) -> None:
        # (level, message) -> set of version ids (empty set = version independent)
        self.items: dict[tuple[str, str], set[str]] = defaultdict(set)

    def add(self, level: str, msg: str, version: str | None = None) -> None:
        s = self.items[(level, msg)]
        if version:
            s.add(version)

    def count(self, level: str) -> int:
        return sum(1 for (lv, _m) in self.items if lv == level)


def fmt_tuple(v) -> Version:
    if isinstance(v, int):
        return (v, 0)
    return (int(v[0]), int(v[1]) if len(v) > 1 else 0)


def lo_hi(entry: dict) -> tuple[Version, Version]:
    """(min, max) of a pack/overlay entry; an int max means 'any minor'."""
    mn = fmt_tuple(entry["min_format"])
    mx = entry["max_format"]
    hi = (mx, 10 ** 9) if isinstance(mx, int) else (int(mx[0]), int(mx[1]) if len(mx) > 1 else 10 ** 9)
    return mn, hi


# ----------------------------------------------------------------------------- helpers
def png_info(path: Path):
    with Image.open(path) as im:
        im.load()
        return im.size, im.mode


def tex_ref_to_path(ref: str) -> str:
    """'minecraft:item/foo' / 'item/foo' -> 'textures/item/foo.png'."""
    ref = ref.split(":", 1)[1] if ":" in ref else ref
    return f"textures/{ref}.png"


def particle_ref_to_path(ref: str) -> str:
    """Particle sprite ids resolve against the particle atlas source directory: textures/particle/."""
    ref = ref.split(":", 1)[1] if ":" in ref else ref
    return f"textures/particle/{ref}.png"


def model_ref_to_path(ref: str) -> str:
    ref = ref.split(":", 1)[1] if ":" in ref else ref
    return f"models/{ref}.json"


def load_json(path: Path, report: Report, rel: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        report.add("ERROR", f"{rel}: invalid JSON ({exc})")
        return None


# ----------------------------------------------------------------------------- main checks
def check_mcmeta(report: Report, ref: Reference, pack: Path) -> dict | None:
    f = pack / "pack.mcmeta"
    if not f.is_file():
        report.add("ERROR", "pack.mcmeta is missing")
        return None
    data = load_json(f, report, "pack.mcmeta")
    if data is None:
        return None
    p = data.get("pack")
    if not isinstance(p, dict):
        report.add("ERROR", "pack.mcmeta: missing 'pack' object")
        return None
    if "description" not in p:
        report.add("ERROR", "pack.mcmeta: pack.description is missing")
    for k in ("min_format", "max_format"):
        if k not in p:
            report.add("ERROR", f"pack.mcmeta: pack.{k} is missing (required since 1.21.9)")
            return None
    if "supported_formats" in p:
        report.add("ERROR", "pack.mcmeta: 'supported_formats' must be absent when the pack does not support pre-1.21.9 versions")
    if "pack_format" in p:
        report.add("WARN", "pack.mcmeta: 'pack_format' is deprecated for 1.21.9+; remove it unless you also target older versions")
    try:
        lo, hi = lo_hi(p)
    except Exception:  # noqa: BLE001
        report.add("ERROR", "pack.mcmeta: min_format/max_format must be an int or [major, minor]")
        return None
    if lo > hi:
        report.add("ERROR", f"pack.mcmeta: min_format {lo} is greater than max_format")
    for v in ref.versions:
        if not (lo <= v.format <= hi):
            report.add("ERROR", f"pack.mcmeta: format range does not include {v.id} (format {v.format[0]}.{v.format[1]})", v.id)

    on_disk = {d.name for d in pack.iterdir() if d.is_dir() and d.name != "assets"}
    listed = set()
    for i, e in enumerate((data.get("overlays") or {}).get("entries", [])):
        name = e.get("directory", "")
        listed.add(name)
        if not OVERLAY_DIR_RE.match(name):
            report.add("ERROR", f"pack.mcmeta: overlay #{i} has an illegal directory name {name!r}")
        if not (pack / name).is_dir():
            report.add("ERROR", f"pack.mcmeta: overlay directory '{name}' does not exist")
        if "formats" in e:
            report.add("ERROR", f"pack.mcmeta: overlay '{name}' must not use legacy 'formats' (pack does not support pre-1.21.9)")
        try:
            olo, ohi = lo_hi(e)
        except Exception:  # noqa: BLE001
            report.add("ERROR", f"pack.mcmeta: overlay '{name}' needs min_format and max_format")
            continue
        if olo < lo or ohi > hi:
            report.add("WARN", f"pack.mcmeta: overlay '{name}' range extends beyond the pack's supported range")
    for stray in sorted(on_disk - listed):
        report.add("WARN", f"directory '{stray}/' is not listed in pack.mcmeta overlays and will be ignored by the game")
    return data


def collect_layers(pack: Path, mcmeta: dict) -> tuple[dict[str, Path], dict[str, dict[str, Path]]]:
    """base: rel-path -> file;  overlays: name -> (rel-path -> file) with rel relative to the overlay root."""
    def walk(root: Path, skip: set[str]) -> dict[str, Path]:
        out = {}
        for f in sorted(root.rglob("*")):
            if f.is_file():
                rel = f.relative_to(root).as_posix()
                if rel.split("/")[0] in skip:
                    continue
                out[rel] = f
        return out

    names = {e["directory"] for e in (mcmeta.get("overlays") or {}).get("entries", []) if "directory" in e}
    base = walk(pack, names)
    overlays = {n: walk(pack / n, set()) for n in names if (pack / n).is_dir()}
    return base, overlays


def effective_files(base, overlays, mcmeta, fmt: Version) -> dict[str, tuple[Path, str]]:
    """Files the game sees on a version: rel-path -> (file, layer-name)."""
    eff = {rel: (p, "base") for rel, p in base.items()}
    for e in (mcmeta.get("overlays") or {}).get("entries", []):
        name = e.get("directory")
        if name not in overlays:
            continue
        try:
            lo, hi = lo_hi(e)
        except Exception:  # noqa: BLE001
            continue
        if lo <= fmt <= hi:
            for rel, p in overlays[name].items():
                eff[rel] = (p, name)
    return eff


def validate_version(report: Report, ref: Reference, vi: int, eff: dict[str, tuple[Path, str]],
                     stats: dict) -> None:
    v = ref.versions[vi]
    vid = v.id
    ns_prefix = "assets/minecraft/"
    pack_has = {rel[len(ns_prefix):] for rel in eff if rel.startswith(ns_prefix)}

    # pass 1: collect texture references made by our own JSON so custom (non-vanilla) textures are allowed
    referenced_textures: set[str] = set()
    parsed: dict[str, object] = {}
    for rel, (p, _layer) in eff.items():
        if not rel.startswith(ns_prefix):
            continue
        sub = rel[len(ns_prefix):]
        if sub.endswith(".json") and (sub.startswith(("models/", "particles/", "items/", "equipment/"))):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                report.add("ERROR", f"{rel}: invalid JSON ({exc})", vid)
                continue
            parsed[sub] = data
            if sub.startswith("models/"):
                for t in (data.get("textures") or {}).values():
                    if isinstance(t, str) and not t.startswith("#"):
                        referenced_textures.add(tex_ref_to_path(t))
            elif sub.startswith("particles/"):
                for t in data.get("textures", []):
                    if isinstance(t, str):
                        referenced_textures.add(particle_ref_to_path(t))

    def texture_exists(path: str) -> bool:
        return ref.has(vi, path) or path in pack_has

    overridden = 0
    for rel, (p, layer) in sorted(eff.items()):
        if rel in ROOT_FILES:
            continue
        where = f"{rel}" + ("" if layer == "base" else f"  [{layer}]")
        if p.name in JUNK:
            report.add("WARN", f"{rel}: junk file", vid)
            continue
        if not NAME_RE.match(rel):
            report.add("ERROR", f"{rel}: path must be lowercase [a-z0-9/._-] only", vid)
        if not rel.startswith(ns_prefix):
            report.add("INFO", f"{rel}: outside assets/minecraft (not checked)", vid)
            continue
        sub = rel[len(ns_prefix):]

        # ------------------------------------------------------------------ PNG
        if sub.endswith(".png"):
            try:
                (w, h), mode = png_info(p)
            except Exception as exc:  # noqa: BLE001
                report.add("ERROR", f"{where}: unreadable PNG ({exc})", vid)
                continue
            if mode not in ("RGBA", "RGB", "LA", "L", "P"):
                report.add("WARN", f"{where}: unusual PNG mode {mode}", vid)
            if not sub.startswith("textures/"):
                continue
            mcmeta_rel = rel + ".mcmeta"
            animated = False
            if mcmeta_rel in eff:
                try:
                    anim = json.loads(eff[mcmeta_rel][0].read_text(encoding="utf-8"))
                    animated = "animation" in anim
                except Exception:  # noqa: BLE001
                    pass
            vanilla = ref.size(vi, sub)
            if vanilla is None:
                if sub not in referenced_textures:
                    report.add("ERROR", f"{where}: no such vanilla texture on this version and nothing references it (dead file / wrong path)", vid)
                continue
            overridden += 1
            vw, vh = vanilla
            if animated:
                aw = None
                try:
                    a = json.loads(eff[mcmeta_rel][0].read_text(encoding="utf-8"))["animation"]
                    aw, ah = a.get("width"), a.get("height")
                except Exception:  # noqa: BLE001
                    ah = None
                fw, fh = (aw or w), (ah or aw or w)
                if w != vw:
                    report.add("ERROR", f"{where}: animated texture width {w} != vanilla {vw}", vid)
                if h % fh != 0 or w % fw != 0:
                    report.add("ERROR", f"{where}: {w}x{h} is not a whole number of {fw}x{fh} frames", vid)
            elif (w, h) != (vw, vh):
                vanilla_animated = ref.has(vi, sub + ".mcmeta") and vh > vw
                if vanilla_animated and (w, h) == (vw, vw):
                    pass                                    # static one-frame stand-in for an animated texture (static variant)
                else:
                    report.add("ERROR", f"{where}: size {w}x{h} != vanilla {vw}x{vh}", vid)

        # --------------------------------------------------------------- .mcmeta
        elif sub.endswith(".png.mcmeta"):
            png_rel = rel[: -len(".mcmeta")]
            if png_rel not in eff:
                report.add("ERROR", f"{where}: .mcmeta has no matching PNG in the pack (the game ignores vanilla art + custom meta)", vid)
            elif eff[png_rel][1] != layer:
                report.add("ERROR", f"{where}: .mcmeta and its PNG live in different layers ({layer} vs {eff[png_rel][1]})", vid)
            try:
                meta = json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                report.add("ERROR", f"{where}: invalid JSON ({exc})", vid)
                continue
            anim = meta.get("animation")
            if isinstance(anim, dict) and png_rel in eff:
                (w, h), _ = png_info(eff[png_rel][0])
                fw = anim.get("width") or w
                fh = anim.get("height") or anim.get("width") or w
                nframes = (h // fh) * (w // fw) if fh and fw else 0
                for fr in anim.get("frames", []):
                    idx = fr["index"] if isinstance(fr, dict) else fr
                    if not isinstance(idx, int) or not (0 <= idx < nframes):
                        report.add("ERROR", f"{where}: animation frame index {idx!r} out of range (0..{nframes - 1})", vid)
                        break
                ft = anim.get("frametime", 1)
                if not isinstance(ft, int) or ft < 1:
                    report.add("ERROR", f"{where}: frametime must be a positive integer", vid)

        # ------------------------------------------------------------------ JSON
        elif sub.endswith(".json"):
            data = parsed.get(sub)
            if sub == "sounds.json":
                data = load_json(p, report, rel)
                for ev in (data or {}):
                    if not ref.has_sound_event(vi, ev):
                        report.add("WARN", f"{where}: sound event '{ev}' does not exist on this version", vid)
                continue
            if data is None:
                if not sub.startswith(("models/", "particles/", "items/", "equipment/")):
                    report.add("INFO", f"{where}: JSON not specifically checked", vid)
                continue
            if sub.startswith("models/"):
                if not isinstance(data, dict):
                    report.add("ERROR", f"{where}: model must be a JSON object", vid)
                    continue
                parent = data.get("parent")
                if parent:
                    pp = model_ref_to_path(parent)
                    builtin = parent.split(":")[-1].startswith(("builtin/", "block/"))
                    if not builtin and not (ref.has(vi, pp) or pp[len("models/"):] in pack_has or pp in pack_has):
                        report.add("ERROR", f"{where}: parent '{parent}' not found on this version", vid)
                for key, t in (data.get("textures") or {}).items():
                    if isinstance(t, str) and not t.startswith("#") and not texture_exists(tex_ref_to_path(t)):
                        report.add("ERROR", f"{where}: texture '{t}' ({key}) not found on this version", vid)
                for ctx, tr in (data.get("display") or {}).items():
                    for field in ("rotation", "translation", "scale"):
                        if field not in tr:
                            continue
                        vals = tr[field]
                        if not (isinstance(vals, list) and len(vals) == 3 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in vals)):
                            report.add("ERROR", f"{where}: display.{ctx}.{field} must be 3 finite numbers", vid)
                        elif field == "scale" and not all(0.02 <= abs(x) <= 8 for x in vals):
                            report.add("ERROR", f"{where}: display.{ctx}.scale {vals} outside sane range 0.02..8", vid)
                        elif field == "translation" and not all(abs(x) <= 80 for x in vals):
                            report.add("ERROR", f"{where}: display.{ctx}.translation {vals} is beyond the game's +-80 clamp", vid)
                if not ref.has(vi, sub):
                    report.add("INFO", f"{where}: new model (not a vanilla override)", vid)
            elif sub.startswith("particles/"):
                if not ref.has(vi, sub):
                    report.add("WARN", f"{where}: particle definition does not exist in vanilla on this version", vid)
                for t in data.get("textures", []):
                    if isinstance(t, str) and not texture_exists(particle_ref_to_path(t)):
                        report.add("ERROR", f"{where}: particle sprite '{t}' not found on this version", vid)
            elif sub.startswith("items/"):
                if not ref.has(vi, sub):
                    report.add("INFO", f"{where}: new item definition", vid)
        else:
            report.add("INFO", f"{where}: file type not specifically checked", vid)

    stats[vid] = {"files": len(eff), "overridden_textures": overridden}


def run(pack: Path, verbose: bool = False, strict: bool = False, quiet: bool = False) -> int:
    """Validate ``pack``; returns a process exit status (0 = OK)."""
    out = (lambda *a, **k: None) if quiet else print
    ref = Reference()
    report = Report()
    out(f"validating {pack} against {', '.join(v.id for v in ref.versions)}\n")

    mcmeta = check_mcmeta(report, ref, pack)
    stats: dict = {}
    if mcmeta is not None:
        if not (pack / "pack.png").is_file():
            report.add("WARN", "pack.png (the pack icon) is missing")
        else:
            (w, h), _ = png_info(pack / "pack.png")
            if w != h:
                report.add("WARN", f"pack.png should be square (is {w}x{h})")
        base, overlays = collect_layers(pack, mcmeta)
        for vi, v in enumerate(ref.versions):
            eff = effective_files(base, overlays, mcmeta, v.format)
            validate_version(report, ref, vi, eff, stats)

    total_bytes = sum(f.stat().st_size for f in pack.rglob("*") if f.is_file()) if pack.exists() else 0

    all_versions = {v.id for v in ref.versions}
    for level in ("ERROR", "WARN", "INFO"):
        if level == "INFO" and not verbose:
            continue
        rows = sorted(((m, vs) for (lv, m), vs in report.items.items() if lv == level))
        for msg, vs in rows:
            tag = "" if not vs else (" (all versions)" if vs == all_versions else f" [{', '.join(sorted(vs))}]")
            print(f"{level:5} {msg}{tag}") if (not quiet or level == "ERROR") else None

    out("\nper-version summary")
    for v in ref.versions:
        s = stats.get(v.id)
        if s:
            out(f"  {v.id:<8} format {v.format[0]}.{v.format[1]:<2}  {s['files']:>4} effective files, "
                f"{s['overridden_textures']:>4} vanilla textures overridden")
    n_err, n_warn = report.count("ERROR"), report.count("WARN")
    out(f"\n{n_err} error(s), {n_warn} warning(s)  |  pack size on disk: {total_bytes / 1024:.0f} KiB")
    if n_err or (strict and n_warn):
        out("FAILED")
        return 1
    out("OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", type=Path, default=config.PACK_DIR)
    ap.add_argument("-v", "--verbose", action="store_true", help="also print INFO notes")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()
    return run(args.pack, args.verbose, args.strict)


if __name__ == "__main__":
    sys.exit(main())
