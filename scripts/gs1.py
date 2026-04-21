"""GS1 GTIN / UPC helpers: check digits, segmented UPC, EAN-13, validation."""

import re

SEGMENTED_UPC = re.compile(r"^(\d{2})-(\d{5})-(\d{5})$")


def gtin13_check_digit(data_12: str) -> int:
    """GS1 GTIN-13 check digit from the first 12 digits (left to right)."""
    total = 0
    for i, ch in enumerate(data_12):
        d = int(ch)
        if i % 2 == 0:
            total += d
        else:
            total += d * 3
    return (10 - (total % 10)) % 10


def gtin12_check_digit(first_11: str) -> int:
    """GS1 GTIN-12 (UPC-A) check digit from the first 11 digits (left to right)."""
    total = 0
    for i, ch in enumerate(first_11):
        d = int(ch)
        if i % 2 == 0:
            total += d * 3
        else:
            total += d
    return (10 - (total % 10)) % 10


def ean8_check_digit(first_seven: str) -> int:
    """GS1 EAN-8 check digit from the first 7 digits (left to right)."""
    total = 0
    for i, ch in enumerate(first_seven):
        d = int(ch)
        if i % 2 == 0:
            total += d * 3
        else:
            total += d
    return (10 - (total % 10)) % 10


def is_valid_ean8(ean8: str) -> bool:
    if len(ean8) != 8 or not ean8.isdigit():
        return False
    return int(ean8[7]) == ean8_check_digit(ean8[:7])


def detect_ean8_from_gtin12_data(data_12: str) -> str | None:
    """If GTIN-12 data is four zeros + valid EAN-8, return the 8-digit code."""
    if len(data_12) != 12 or not data_12.isdigit() or not data_12.startswith("0000"):
        return None
    candidate = data_12[-8:]
    if is_valid_ean8(candidate):
        return candidate
    return None


def ean13_to_upc12(ean13: str) -> str:
    if len(ean13) == 13 and ean13.isdigit() and ean13[0] == "0":
        return ean13[1:]
    return ""


def is_valid_gtin13(code: str) -> bool:
    if len(code) != 13 or not code.isdigit():
        return False
    return int(code[12]) == gtin13_check_digit(code[:12])


def from_segmented_upc(upc: str) -> tuple[str, str] | None:
    m = SEGMENTED_UPC.match((upc or "").strip())
    if not m:
        return None
    seg1, seg2, seg3 = m.group(1), m.group(2), m.group(3)
    data_12 = seg1 + seg2 + seg3
    chk = gtin13_check_digit(data_12)
    return data_12, data_12 + str(chk)


def fallback_from_digits(upc: str) -> tuple[str, str]:
    digits = re.sub(r"\D", "", (upc or "").strip())
    if not digits:
        return "", ""
    if len(digits) >= 13:
        block = digits[-13:] if len(digits) > 13 else digits[:13]
        if len(block) == 13 and block.isdigit():
            data_12 = block[:12]
            canonical = data_12 + str(gtin13_check_digit(data_12))
            return data_12, canonical
    digits = digits.zfill(12)
    if len(digits) > 12:
        digits = digits[-12:]
    if len(digits) != 12 or not digits.isdigit():
        return digits, digits
    chk = gtin13_check_digit(digits)
    return digits, digits + str(chk)


def barcode_columns(upc: str) -> tuple[str, str, str, str, str, bool]:
    """UPCA, UPCA_No_Check_Digit, UPC12, UPC12_No_Check_Digit, EAN8, Is_EAN8."""
    parsed = from_segmented_upc(upc)
    if parsed:
        data_12, ean13 = parsed
    else:
        data_12, ean13 = fallback_from_digits(upc)

    upc12 = ean13_to_upc12(ean13)
    upc12_no_check = ""
    if len(upc12) == 12 and upc12.isdigit():
        upc12_no_check = upc12[:11]

    ean8 = detect_ean8_from_gtin12_data(data_12) or ""
    is_ean8 = bool(ean8)

    return ean13, data_12, upc12, upc12_no_check, ean8, is_ean8


def is_valid_barcode(upca: str) -> bool:
    s = (upca or "").strip()
    if not s.isdigit():
        return False
    if len(s) == 13:
        return int(s[12]) == gtin13_check_digit(s[:12])
    if len(s) == 12:
        return int(s[11]) == gtin12_check_digit(s[:11])
    return False
