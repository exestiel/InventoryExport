"""Extract UPC, Description, dept, size, UOM, Regular Price from multi-line inventory CSV export."""

import argparse
import csv
import sys
from pathlib import Path

from io_utils import UPC_RE, open_text_read

_ROOT = Path(__file__).resolve().parent.parent
INPUT_DEFAULT = _ROOT / "source" / "inventory.csv"
OUTPUT_DEFAULT = _ROOT / "source" / "extracted.csv"


def _parse_args() -> tuple[Path, Path]:
    p = argparse.ArgumentParser(
        description="Extract UPC columns from raw inventory CSV into a flat file.",
    )
    p.add_argument("input_pos", nargs="?", default=None, metavar="input")
    p.add_argument("output_pos", nargs="?", default=None, metavar="output")
    p.add_argument("-i", "--input", type=Path, default=None, dest="input_flag")
    p.add_argument("-o", "--output", type=Path, default=None, dest="output_flag")
    args = p.parse_args()
    in_path = args.input_flag or (
        Path(args.input_pos) if args.input_pos is not None else INPUT_DEFAULT
    )
    out_path = args.output_flag or (
        Path(args.output_pos) if args.output_pos is not None else OUTPUT_DEFAULT
    )
    return in_path, out_path


def main() -> int:
    in_path, out_path = _parse_args()

    if not in_path.is_file():
        print(f"Input not found: {in_path}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open_text_read(in_path) as f_in, open(
        out_path, "w", encoding="utf-8-sig", newline=""
    ) as f_out:
        writer = csv.writer(f_out)
        writer.writerow(
            ["upc", "Description", "dept", "size", "UOM", "regular price"]
        )
        reader = csv.reader(f_in)
        for row in reader:
            for i, cell in enumerate(row):
                if UPC_RE.match(cell.strip()):
                    if i + 5 < len(row):
                        chunk = row[i : i + 6]
                        writer.writerow(chunk)
                        count += 1
                    break

    print(f"Wrote {count} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
