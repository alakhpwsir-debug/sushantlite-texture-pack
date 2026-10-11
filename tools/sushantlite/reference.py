"""Loader for the compact vanilla-asset index written by tools/fetch_reference.py."""
from __future__ import annotations

import gzip
import json
from dataclasses import dataclass

from . import config


@dataclass(frozen=True)
class VersionInfo:
    id: str
    format: tuple[int, int]      # (major, minor) resource pack format
    released: str = ""


class Reference:
    def __init__(self) -> None:
        meta = json.loads((config.REFERENCE_DIR / "versions.json").read_text(encoding="utf-8"))
        self.versions = [VersionInfo(v["id"], tuple(v["resource_pack_format"]), v.get("released", ""))
                         for v in meta["versions"]]
        # path -> (mask, size-field)
        self._entries: dict[str, tuple[str, str]] = {}
        with gzip.open(config.REFERENCE_DIR / "vanilla-index.tsv.gz", "rt", encoding="utf-8") as fh:
            header = fh.readline().rstrip("\n").split("\t")[1:]
            if header != [v.id for v in self.versions]:
                raise RuntimeError("vanilla-index.tsv.gz and versions.json disagree; re-run tools/fetch_reference.py")
            for line in fh:
                mask, size, path = line.rstrip("\n").split("\t", 2)
                self._entries[path] = (mask, size)

    # ------------------------------------------------------------------ queries
    def has(self, vi: int, path: str) -> bool:
        e = self._entries.get(path)
        return bool(e) and e[0][vi] == "1"

    def size(self, vi: int, path: str) -> tuple[int, int] | None:
        e = self._entries.get(path)
        if not e or e[0][vi] != "1":
            return None
        field = e[1]
        if "," in field:
            field = field.split(",")[vi]
        if "x" not in field or field in ("x", "-"):
            return None
        w, h = field.split("x")
        return int(w), int(h)

    def has_sound_event(self, vi: int, event: str) -> bool:
        return self.has(vi, f"sound-event:{event}")

    def paths(self, vi: int, prefix: str = "") -> list[str]:
        return [p for p, (m, _s) in self._entries.items() if m[vi] == "1" and p.startswith(prefix)]
