"""Load department id → name map from optional multiline dep.csv."""

import csv
import re
from pathlib import Path

from io_utils import open_text_read

# First row treated as header when column 0 / 1 look like typical export headers.
_COL0_HEADER = frozenset(
    {
        "id",
        "dept_id",
        "department_id",
        "department id",
        "code",
        "#",
        "dept",
        "dep",
        "department code",
        "deptcode",
    }
)
_COL1_HEADER = frozenset(
    {
        "name",
        "dept_name",
        "deptname",
        "department_name",
        "department name",
        "description",
        "title",
        "dept name",
        "department",
    }
)


def _norm_cell(s: str) -> str:
    return " ".join(s.strip().split()).lower()


def _header_tokens(n: str) -> list[str]:
    """Alphanumeric tokens only; avoids 'id' matching inside 'valid' + 'dept'."""
    return re.findall(r"[a-z0-9]+", n)


def _cell_is_id_header(n: str) -> bool:
    if n in _COL0_HEADER:
        return True
    tok = _header_tokens(n)
    if "id" in tok and ("dept" in tok or "department" in tok):
        return True
    return False


def _cell_is_name_header(n: str) -> bool:
    if n in _COL1_HEADER:
        return True
    if "name" in n and not _cell_is_id_header(n):
        return True
    if "desc" in n and not _cell_is_id_header(n):
        return True
    return False


def _looks_like_header_row(row: list[str]) -> bool:
    if len(row) < 2:
        return False
    norms = [_norm_cell(c) for c in row]
    has_id = any(_cell_is_id_header(n) for n in norms)
    has_name = any(_cell_is_name_header(n) for n in norms)
    if has_id and has_name:
        return True
    a, b = norms[0], norms[1]
    if ("dept" in a or "department" in a) and "id" in _header_tokens(a):
        return _cell_is_name_header(b) or b in _COL1_HEADER
    return False


def _department_report_id_name_columns(row: list[str]) -> tuple[int, int] | None:
    """POS 'Department Report' export: id and name follow a literal 'Group' column."""
    if not row or _norm_cell(row[0]) != "department report":
        return None
    for j, cell in enumerate(row):
        if _norm_cell(cell) == "group" and j + 2 < len(row):
            return j + 1, j + 2
    return None


def _id_name_column_indices(header_row: list[str]) -> tuple[int, int]:
    """Which columns hold id vs name for header row. Defaults (0, 1) if unclear."""
    id_cols = [j for j, c in enumerate(header_row) if _cell_is_id_header(_norm_cell(c))]
    name_cols = [j for j, c in enumerate(header_row) if _cell_is_name_header(_norm_cell(c))]
    for i in id_cols:
        for n in name_cols:
            if n != i:
                return i, n
    return 0, 1


def load_department_map(path: Path) -> dict[str, str]:
    """Return id → display name. Empty dict if file missing or has no usable rows.

    Uses csv.reader over the full file (handles quoted fields with embedded
    newlines). POS Department Report exports (first cell + Group column) use the
    two columns after Group as id and name. Otherwise the first row
    may be a header row (heuristic); remaining rows use detected id/name column
    indices (or 0 and 1). Later duplicate ids overwrite.
    """
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    try:
        with open_text_read(path) as f:
            reader = csv.reader(f)
            rows = list(reader)
    except OSError:
        return {}
    if not rows:
        return {}
    report_cols = _department_report_id_name_columns(rows[0])
    if report_cols is not None:
        start = 0
        id_i, name_i = report_cols
    elif _looks_like_header_row(rows[0]):
        start = 1
        id_i, name_i = _id_name_column_indices(rows[0])
    else:
        start = 0
        id_i, name_i = 0, 1
    for row in rows[start:]:
        if max(id_i, name_i) >= len(row):
            continue
        key = row[id_i].strip()
        val = row[name_i].strip()
        if not key:
            continue
        out[key] = val
    return out
