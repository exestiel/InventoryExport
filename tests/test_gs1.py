"""Unit tests for scripts/gs1.py."""

import gs1


def test_gtin13_check_digit_known_vector():
    # 12 payload digits -> 13th check digit (GS1 weights for EAN-13)
    assert gs1.gtin13_check_digit("400638133393") == 1


def test_from_segmented_upc():
    data_12, ean13 = gs1.from_segmented_upc("01-23456-78901")
    assert data_12 == "012345678901"
    assert len(ean13) == 13
    assert ean13.isdigit()
    assert int(ean13[12]) == gs1.gtin13_check_digit(ean13[:12])


def test_barcode_columns_segmented():
    upca, no_chk, upc12, upc12_no_chk, ean8, is_ean8 = gs1.barcode_columns(
        "01-23456-78901"
    )
    assert len(upca) == 13
    assert no_chk == "012345678901"
    assert upc12 == upca[1:] if upca.startswith("0") else ""
    if len(upc12) == 12:
        assert len(upc12_no_chk) == 11
    assert ean8 == ""
    assert is_ean8 is False


def test_ean8_check_digit_known_vector():
    # GS1 example-style EAN-8: 96385074 (7 payload + check)
    assert gs1.ean8_check_digit("9638507") == 4
    assert gs1.is_valid_ean8("96385074")
    assert not gs1.is_valid_ean8("96385075")


def test_detect_ean8_from_gtin12_data():
    assert gs1.detect_ean8_from_gtin12_data("000096385074") == "96385074"
    assert gs1.detect_ean8_from_gtin12_data("000096385075") is None
    assert gs1.detect_ean8_from_gtin12_data("100096385074") is None
    assert gs1.detect_ean8_from_gtin12_data("123456789012") is None


def test_barcode_columns_ean8_segmented():
    # 00 + 00963 + 85074 -> GTIN-12 000096385074 (EAN-8 96385074)
    upca, no_chk, upc12, upc12_no_chk, ean8, is_ean8 = gs1.barcode_columns(
        "00-00963-85074"
    )
    assert no_chk == "000096385074"
    assert ean8 == "96385074"
    assert is_ean8 is True
    assert len(upca) == 13


def test_is_valid_barcode_gtin13():
    assert gs1.is_valid_barcode("4006381333931")


def test_is_valid_barcode_gtin12():
    # Valid UPC-A (12 digits) — check digit must match gtin12 algorithm
    first_11 = "03600024145"
    chk = gs1.gtin12_check_digit(first_11)
    code = first_11 + str(chk)
    assert len(code) == 12
    assert gs1.is_valid_barcode(code)


def test_is_valid_barcode_rejects_bad_check():
    assert not gs1.is_valid_barcode("4006381333930")
    assert not gs1.is_valid_barcode("abc")


def test_is_valid_gtin13():
    assert gs1.is_valid_gtin13("4006381333931")
    assert not gs1.is_valid_gtin13("4006381333930")
