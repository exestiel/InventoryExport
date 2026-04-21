"""echo.convert — validate GS1 check digits on the UPCA column (GTIN-13 EAN-13 or GTIN-12 UPC-A)."""

import argparse
import csv
import sys
from pathlib import Path

from gs1 import is_valid_barcode

_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = _ROOT / "result" / "Inventory_Final.csv"
DEFAULT_INVALID_OUT = _ROOT / "result" / "Inventory_Final_check_invalid.csv"


def _parse_args() -> tuple[Path, Path]:
    p = argparse.ArgumentParser(
        description="echo.convert — validate GS1 check digits on UPCA; write invalid rows to a file.",
    )
    p.add_argument(
        "input_pos",
        nargs="?",
        default=None,
        metavar="input",
        help="input CSV with UPCA column",
    )
    p.add_argument(
        "invalid_out_pos",
        nargs="?",
        default=None,
        metavar="invalid_out",
        help="where to write invalid/bad-format rows",
    )
    p.add_argument("-i", "--input", type=Path, default=None, dest="input_flag")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        dest="invalid_flag",
        help="invalid rows output CSV (overrides positional)",
    )
    args = p.parse_args()
    in_path = args.input_flag or (
        Path(args.input_pos) if args.input_pos is not None else DEFAULT_IN
    )
    invalid_out = args.invalid_flag or (
        Path(args.invalid_out_pos)
        if args.invalid_out_pos is not None
        else DEFAULT_INVALID_OUT
    )
    return in_path, invalid_out


def main() -> int:
    in_path, invalid_out = _parse_args()

    if not in_path.is_file():
        print(f"Input not found: {in_path}", file=sys.stderr)
        return 1

    total = 0
    valid = 0
    invalid = 0
    bad_format = 0

    invalid_rows = []

    with open(in_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames or "UPCA" not in fieldnames:
            print("Expected a header row with a 'UPCA' column.", file=sys.stderr)
            return 1
        for row in reader:
            total += 1
            upca = (row.get("UPCA") or "").strip()
            if len(upca) not in (12, 13) or not upca.isdigit():
                bad_format += 1
                invalid_rows.append(row)
                continue
            if is_valid_barcode(upca):
                valid += 1
            else:
                invalid += 1
                invalid_rows.append(row)

    print(f"File: {in_path}")
    print(f"Rows read: {total}")
    print(f"Valid GS1 check digit (GTIN-12 or GTIN-13): {valid}")
    print(f"Invalid check digit:                      {invalid}")
    print(f"Bad format (not 12 or 13 digits):        {bad_format}")

    if invalid_rows:
        invalid_out.parent.mkdir(parents=True, exist_ok=True)
        with open(invalid_out, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(invalid_rows)
        print(f"Wrote {len(invalid_rows)} invalid/bad rows to {invalid_out}")
    else:
        print("No invalid rows to write.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
