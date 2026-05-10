import pytest

from contract_validator import is_valid_contract


@pytest.mark.parametrize(
    "value",
    [
        "HB-123456.2025",
        "AB-000001.2024",
        "ZZ-999999.2035",
        "XX-555555.2027",
        "QQ-123456.2030",
    ],
)
def test_valid_contract(value):
    assert is_valid_contract(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "hb-123456.2025",
        "HB-12345.2025",
        "HB-123456.2023",
        "HB123456.2025",
        "Hb-123456.2025",
        "HB-1234567.2025",
        "HB-123456.20236",
        "HB-123456.2036",
        "H-123456.2025",
        "HB--123456.2025",
        "HB-123456.2025.1",
        "",
    ],
)
def test_invalid_contract(value):
    assert is_valid_contract(value) is False


@pytest.mark.parametrize(
    "year,expected",
    [
        (2023, False),
        (2024, True),
        (2025, True),
        (2035, True),
        (2036, False),
    ],
)
def test_year_boundaries(year, expected):
    value = f"HB-123456.{year}"
    assert is_valid_contract(value) is expected
