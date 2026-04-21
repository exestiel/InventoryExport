"""Shared CSV/text helpers for inventory scripts."""

import re
from pathlib import Path

UPC_RE = re.compile(r"^\d{2}-\d{5}-\d{5}$")


def open_text_read(path: Path):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return open(path, "r", encoding=enc, newline="")
        except UnicodeDecodeError:
            continue
    return open(path, "r", encoding="utf-8-sig", errors="replace", newline="")
