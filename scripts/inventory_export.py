"""Parse inventory export CSV and write final file with UPC + barcode fields.

Targets typical multi-line retail/POS inventory CSV exports: finds rows with
NN-YYYYY-ZZZZZ item codes and outputs EAN-13 / US UPC-12 derived fields.
"""

import argparse
import csv
import sys
from pathlib import Path

from dept_map import load_department_map
from gs1 import barcode_columns
from io_utils import UPC_RE, open_text_read

_ROOT = Path(__file__).resolve().parent.parent
INPUT_DEFAULT = _ROOT / "source" / "inventory.csv"
OUTPUT_DEFAULT = _ROOT / "result" / "Inventory_Final.csv"
DEPT_MAP_DEFAULT = _ROOT / "source" / "dep.csv"

OUT_FIELDS = [
    "UPC",
    "UPCA",
    "UPCA_No_Check_Digit",
    "UPC12",
    "UPC12_No_Check_Digit",
    "Description",
    "Dept_Id",
    "DeptName",
    "Size",
    "UOM",
    "Regular Price",
]


def _parse_args() -> tuple[Path, Path, Path]:
    p = argparse.ArgumentParser(
        description="Parse inventory CSV and write UPC / barcode columns.",
    )
    p.add_argument(
        "input_pos",
        nargs="?",
        default=None,
        metavar="input",
        help="input CSV path (default: source/inventory.csv)",
    )
    p.add_argument(
        "output_pos",
        nargs="?",
        default=None,
        metavar="output",
        help="output CSV path (default: result/Inventory_Final.csv)",
    )
    p.add_argument(
        "-i",
        "--input",
        type=Path,
        default=None,
        dest="input_flag",
        help="input CSV; overrides positional input if set",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        dest="output_flag",
        help="output CSV; overrides positional output if set",
    )
    p.add_argument(
        "--dept-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="department id→name CSV (default: source/dep.csv); ignored if missing",
    )
    args = p.parse_args()
    in_path = args.input_flag or (
        Path(args.input_pos) if args.input_pos is not None else INPUT_DEFAULT
    )
    out_path = args.output_flag or (
        Path(args.output_pos) if args.output_pos is not None else OUTPUT_DEFAULT
    )
    dept_path = args.dept_file if args.dept_file is not None else DEPT_MAP_DEFAULT
    return in_path, out_path, dept_path


def main() -> int:
    in_path, out_path, dept_path = _parse_args()

    if not in_path.is_file():
        print(f"Input not found: {in_path}", file=sys.stderr)
        return 1

    dept_map = load_department_map(dept_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open_text_read(in_path) as f_in, open(
        out_path, "w", encoding="utf-8-sig", newline=""
    ) as f_out:
        writer = csv.DictWriter(f_out, fieldnames=OUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        reader = csv.reader(f_in)
        for row in reader:
            for i, cell in enumerate(row):
                if UPC_RE.match(cell.strip()):
                    if i + 5 >= len(row):
                        break
                    upc = row[i].strip()
                    desc = row[i + 1]
                    dept_raw = row[i + 2].strip()
                    size = row[i + 3]
                    uom = row[i + 4]
                    reg_price = row[i + 5]
                    upca, upca_no_chk, upc12, upc12_no_chk = barcode_columns(upc)
                    dept_display = dept_map.get(dept_raw, dept_raw)
                    writer.writerow(
                        {
                            "UPC": upc,
                            "UPCA": upca,
                            "UPCA_No_Check_Digit": upca_no_chk,
                            "UPC12": upc12,
                            "UPC12_No_Check_Digit": upc12_no_chk,
                            "Description": desc,
                            "Dept_Id": dept_raw,
                            "DeptName": dept_display,
                            "Size": size,
                            "UOM": uom,
                            "Regular Price": reg_price,
                        }
                    )
                    count += 1
                    break

    print(f"Wrote {count} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
