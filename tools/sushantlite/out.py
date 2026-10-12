"""Output helper: writes generated files into the pack and tracks ownership.

The generator "owns" every file it writes (recorded in tools/generated-files.txt).
On the next run, files it produced earlier but no longer produces are removed,
while anything listed in tools/locked.txt (hand-edited art) is never touched.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from . import config
from .sprite import Sprite


class PackWriter:
    def __init__(self, root: Path | None = None, partial: bool = False):
        self.root = root or config.PACK_DIR
        self.written: set[str] = set()      # pack-relative posix paths produced this run
        self.skipped_locked: list[str] = []
        self.locked = self._read_list(config.LOCKED_FILE)
        # A partial run (--only) re-runs some generators; files of the others stay as they were.
        self.partial = partial
        self._carried = self._read_list(config.GENERATED_MANIFEST) if partial else set()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _read_list(path: Path) -> set[str]:
        if not path.exists():
            return set()
        return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.startswith("#")}

    def _target(self, rel: str, overlay: str | None) -> tuple[str, Path]:
        full_rel = f"{overlay}/{rel}" if overlay else rel
        return full_rel, self.root / full_rel

    def _claim(self, full_rel: str, path: Path) -> bool:
        if not config.included(full_rel):         # outside the active profile's scope: neither written nor owned
            return False
        if full_rel in self.locked and path.exists():
            self.skipped_locked.append(full_rel)
            self.written.add(full_rel)       # still "ours" so it is not cleaned up
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        self.written.add(full_rel)
        return True

    # ------------------------------------------------------------------- writers
    def png(self, rel: str, art, overlay: str | None = None) -> None:
        """Write a PNG.  ``art`` is a Sprite or a PIL image."""
        full_rel, path = self._target(rel, overlay)
        if not self._claim(full_rel, path):
            return
        img = art.to_image() if isinstance(art, Sprite) else art
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.save(path, format="PNG", optimize=True)

    def json(self, rel: str, obj, overlay: str | None = None, indent: int | None = 2) -> None:
        full_rel, path = self._target(rel, overlay)
        if not self._claim(full_rel, path):
            return
        text = json.dumps(obj, indent=indent, ensure_ascii=False)
        path.write_text(text + "\n", encoding="utf-8", newline="\n")

    def text(self, rel: str, content: str, overlay: str | None = None) -> None:
        full_rel, path = self._target(rel, overlay)
        if not self._claim(full_rel, path):
            return
        path.write_text(content, encoding="utf-8", newline="\n")

    def animated_png(self, rel: str, frames: Image.Image, animation: dict | None = None,
                     overlay: str | None = None) -> None:
        """Write an animation strip plus its .mcmeta ({"animation": {...}})."""
        self.png(rel, frames, overlay)
        self.json(rel + ".mcmeta", {"animation": animation or {}}, overlay)

    def used_overlays(self) -> set[str]:
        """Names of overlay directories that hold at least one generated file (this run, or -- on a
        partial run -- an earlier one), so ``pack.mcmeta`` never drops an overlay by accident."""
        files = self.written | self._carried
        return {name for name in config.OVERLAYS
                if any(rel.startswith(name + "/") for rel in files)}

    # ------------------------------------------------------------------ finishing
    def finalize(self, partial: bool = False) -> tuple[int, int]:
        """Remove stale files from the previous run and persist the manifest.

        With ``partial=True`` (a run restricted with --only) nothing is deleted and the
        previous manifest is kept, so a partial run can never wipe other generators' files.

        Returns (files_written, files_removed).
        """
        previous = self._read_list(config.GENERATED_MANIFEST)
        if partial:
            self.written |= previous
            previous = set()
        removed = 0
        for rel in sorted(previous - self.written):
            if rel in self.locked:
                continue
            p = self.root / rel
            if p.is_file():
                p.unlink()
                removed += 1
        # prune empty directories (deepest first)
        for d in sorted((p for p in self.root.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
            try:
                d.rmdir()
            except OSError:
                pass
        header = ("# Files produced by tools/generate.py -- do not edit by hand.\n"
                  "# To keep a hand-edited file, add its pack-relative path to tools/locked.txt.\n")
        config.GENERATED_MANIFEST.write_text(header + "\n".join(sorted(self.written)) + "\n", encoding="utf-8")
        return len(self.written), removed
