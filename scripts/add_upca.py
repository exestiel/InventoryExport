"""Second pass: read extracted inventory CSV and add EAN-13 (GTIN-13) from upc.

Hyphenated source format NN-YYYYY-ZZZZZ is treated as the first 12 digits of EAN-13
(GTIN-13) *without* the check digit: concatenate segments, then append the GS1
GTIN-13 check digit (13th digit).

Weights for check digit: from the left, positions 1,3,5,... x1 and 2,4,6,... x3.

UPC12: US GTIN-12 (12-digit UPC-A) = EAN-13 with leading zero removed when the
GTIN-13 begins with 0 (same item, common US barcode form).
"""

import argparse
import csv
import sys
from pathlib import Path

from gs1 import (
    ean13_to_upc12,
    fallback_from_digits,
    from_segmented_upc,
    is_valid_gtin13,
)

_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = _ROOT / "source" / "extracted.csv"
DEFAULT_OUT = _ROOT / "result" / "extracted_with_upca.csv"


def _parse_args() -> tuple[Path, Path]:
    p = argparse.ArgumentParser(
        description="Add UPCA (EAN-13) and UPC12 columns to extracted inventory CSV.",
    )
    p.add_argument("input_pos", nargs="?", default=None, metavar="input")
    p.add_argument("output_pos", nargs="?", default=None, metavar="output")
    p.add_argument("-i", "--input", type=Path, default=None, dest="input_flag")
    p.add_argument("-o", "--output", type=Path, default=None, dest="output_flag")
    args = p.parse_args()
    in_path = args.input_flag or (
        Path(args.input_pos) if args.input_pos is not None else DEFAULT_IN
    )
    out_path = args.output_flag or (
        Path(args.output_pos) if args.output_pos is not None else DEFAULT_OUT
    )
    return in_path, out_path


def main() -> int:
    in_path, out_path = _parse_args()

    if not in_path.is_file():
        print(f"Input not found: {in_path}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(in_path, "r", encoding="utf-8-sig", newline="") as f_in, open(
        out_path, "w", encoding="utf-8-sig", newline=""
    ) as f_out:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames or "upc" not in reader.fieldnames:
            print("Expected a header row with an 'upc' column.", file=sys.stderr)
            return 1
        skip = {"upc", "UPCA", "UPC12", "UPCA_no_check_digit", "check_digit_ok"}
        fields = ["upc", "UPCA", "UPC12", "UPCA_no_check_digit", "check_digit_ok"] + [
            h for h in reader.fieldnames if h not in skip
        ]
        writer = csv.DictWriter(f_out, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            upc = row.get("upc", "")
            parsed = from_segmented_upc(upc)
            if parsed:
                data_12, ean13 = parsed
            else:
                data_12, ean13 = fallback_from_digits(upc)

            row["UPCA"] = ean13
            row["UPC12"] = ean13_to_upc12(ean13)
            row["UPCA_no_check_digit"] = data_12
            row["check_digit_ok"] = bool(ean13) and is_valid_gtin13(ean13)
            writer.writerow(row)
            count += 1

    print(f"Wrote {count} rows (UPCA=EAN-13, UPC12=GTIN-12 when leading 0) to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
