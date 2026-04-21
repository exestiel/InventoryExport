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
    upca, no_chk, upc12, upc12_no_chk, upce, is_upce, upce_exp = gs1.barcode_columns(
        "01-23456-78901"
    )
    assert len(upca) == 13
    assert no_chk == "012345678901"
    assert upc12 == upca[1:] if upca.startswith("0") else ""
    if len(upc12) == 12:
        assert len(upc12_no_chk) == 11
    assert upce == ""
    assert is_upce is False
    assert upce_exp == ""


def test_expand_upce_to_upca12_known_vectors():
    # Stack Overflow / GS1-style expansion examples
    assert gs1.expand_upce_to_upca12("02345673") == "023456000073"
    assert gs1.expand_upce_to_upca12("07832309") == "078000003239"
    assert gs1.expand_upce_to_upca12("06397126") == "063200009716"


def test_is_valid_upce():
    assert gs1.is_valid_upce("02345673")
    assert gs1.is_valid_upce("07832309")
    assert not gs1.is_valid_upce("02345674")


def test_detect_upce_from_gtin12_data():
    assert gs1.detect_upce_from_gtin12_data("000002345673") == "02345673"
    assert gs1.detect_upce_from_gtin12_data("000002345674") is None
    assert gs1.detect_upce_from_gtin12_data("100002345673") is None
    assert gs1.detect_upce_from_gtin12_data("123456789012") is None


def test_barcode_columns_upce_segmented():
    # 00 + 00023 + 45673 -> GTIN-12 000002345673 (UPC-E 02345673)
    upca, no_chk, upc12, upc12_no_chk, upce, is_upce, upce_exp = gs1.barcode_columns(
        "00-00023-45673"
    )
    assert no_chk == "000002345673"
    assert upce == "02345673"
    assert is_upce is True
    assert upce_exp == "023456000073"
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
