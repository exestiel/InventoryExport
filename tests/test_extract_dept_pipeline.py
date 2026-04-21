"""Integration-style tests for extract_inventory / add_upca with dep.csv."""

import csv
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def test_extract_and_add_upca_apply_dep_map(tmp_path: Path):
    inv = tmp_path / "inventory.csv"
    dep = tmp_path / "dep.csv"
    ext = tmp_path / "extracted.csv"
    final = tmp_path / "out.csv"
    inv.write_text("00-00000-00001,Item A,42,0,,1.00\n", encoding="utf-8")
    dep.write_text("42,Hardware\n", encoding="utf-8")

    r1 = subprocess.run(
        [
            sys.executable,
            str(_REPO / "scripts" / "extract_inventory.py"),
            "-i",
            str(inv),
            "-o",
            str(ext),
            "--dept-file",
            str(dep),
        ],
        cwd=str(_REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r1.returncode == 0, r1.stderr

    with ext.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["Dept_Id"] == "42"
    assert rows[0]["DeptName"] == "Hardware"

    r2 = subprocess.run(
        [
            sys.executable,
            str(_REPO / "scripts" / "add_upca.py"),
            "-i",
            str(ext),
            "-o",
            str(final),
            "--dept-file",
            str(dep),
        ],
        cwd=str(_REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r2.returncode == 0, r2.stderr

    with final.open(encoding="utf-8-sig", newline="") as f:
        rows2 = list(csv.DictReader(f))
    assert rows2[0]["Dept_Id"] == "42"
    assert rows2[0]["DeptName"] == "Hardware"
    assert rows2[0]["UPCA"]
