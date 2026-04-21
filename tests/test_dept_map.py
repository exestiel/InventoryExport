"""Tests for scripts/dept_map.py."""

import csv
from pathlib import Path

import dept_map


def test_missing_file_returns_empty(tmp_path: Path):
    assert dept_map.load_department_map(tmp_path / "nope.csv") == {}


def test_no_header_two_columns(tmp_path: Path):
    p = tmp_path / "dep.csv"
    p.write_text("10,Grocery\n20,Deli\n", encoding="utf-8")
    m = dept_map.load_department_map(p)
    assert m == {"10": "Grocery", "20": "Deli"}


def test_header_row_skipped(tmp_path: Path):
    p = tmp_path / "dep.csv"
    p.write_text("dept_id,name\n10,Grocery\n", encoding="utf-8")
    m = dept_map.load_department_map(p)
    assert m == {"10": "Grocery"}


def test_quoted_field_with_newline(tmp_path: Path):
    p = tmp_path / "dep.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name"])
        w.writerow(["1", "First line\nSecond line"])
        w.writerow(["2", "Plain"])
    m = dept_map.load_department_map(p)
    assert m["1"] == "First line\nSecond line"
    assert m["2"] == "Plain"


def test_duplicate_id_last_wins(tmp_path: Path):
    p = tmp_path / "dep.csv"
    p.write_text("1,A\n1,B\n", encoding="utf-8")
    assert dept_map.load_department_map(p) == {"1": "B"}


def test_department_id_style_header(tmp_path: Path):
    p = tmp_path / "dep.csv"
    p.write_text("Department ID,Department Name\n5,Housewares\n", encoding="utf-8")
    m = dept_map.load_department_map(p)
    assert m == {"5": "Housewares"}


def test_header_uses_deptname_column(tmp_path: Path):
    p = tmp_path / "dep.csv"
    p.write_text("Department ID,DeptName\n7,Bakery\n", encoding="utf-8")
    assert dept_map.load_department_map(p) == {"7": "Bakery"}


def test_wide_header_reordered_columns(tmp_path: Path):
    p = tmp_path / "dep.csv"
    p.write_text(
        "Note,Department Name,Department ID,Extra\n,Produce,12,\n,Deli,20,\n",
        encoding="utf-8",
    )
    m = dept_map.load_department_map(p)
    assert m == {"12": "Produce", "20": "Deli"}


def test_pos_department_report_uses_group_columns(tmp_path: Path):
    """Wide POS export: id/name sit after 'Group', not in column 0/1."""
    p = tmp_path / "dep.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "Department Report",
                "Store",
                "x",
                "y",
                "Group",
                "10",
                "CANDY",
                "tail",
            ]
        )
        w.writerow(
            [
                "Department Report",
                "Store",
                "x",
                "y",
                "Group",
                "11",
                "WATER",
                "tail",
            ]
        )
    assert dept_map.load_department_map(p) == {"10": "CANDY", "11": "WATER"}
