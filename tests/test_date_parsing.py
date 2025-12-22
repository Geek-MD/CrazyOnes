#!/usr/bin/env python3
"""
Test script for date parsing functionality.
"""

from scripts.utils import parse_date_to_iso


def test_parse_english_dates():
    """Test parsing English date formats."""
    print("Testing English date formats...")

    assert parse_date_to_iso("11 Dec 2023") == "2023-12-11"
    assert parse_date_to_iso("11 December 2023") == "2023-12-11"
    assert parse_date_to_iso("1 Jan 2024") == "2024-01-01"

    print("  ✓ English dates parsed correctly")


def test_parse_spanish_dates():
    """Test parsing Spanish date formats."""
    print("\nTesting Spanish date formats...")

    assert parse_date_to_iso("09 de enero de 2024") == "2024-01-09"
    assert parse_date_to_iso("22 de enero de 2024") == "2024-01-22"
    assert parse_date_to_iso("11 dic 2023") == "2023-12-11"
    assert parse_date_to_iso("11 de diciembre de 2023") == "2023-12-11"

    print("  ✓ Spanish dates parsed correctly")


def test_parse_french_dates():
    """Test parsing French date formats."""
    print("\nTesting French date formats...")

    assert parse_date_to_iso("11 déc. 2023") == "2023-12-11"
    assert parse_date_to_iso("11 décembre 2023") == "2023-12-11"

    print("  ✓ French dates parsed correctly")


def test_parse_german_dates():
    """Test parsing German date formats."""
    print("\nTesting German date formats...")

    assert parse_date_to_iso("11. Dez. 2023") == "2023-12-11"
    assert parse_date_to_iso("11. Dezember 2023") == "2023-12-11"

    print("  ✓ German dates parsed correctly")


def test_parse_iso_dates():
    """Test that ISO dates pass through unchanged."""
    print("\nTesting ISO date formats...")

    assert parse_date_to_iso("2024-01-09") == "2024-01-09"
    assert parse_date_to_iso("2023-12-11") == "2023-12-11"

    print("  ✓ ISO dates pass through correctly")


def test_invalid_dates():
    """Test that invalid dates return original string."""
    print("\nTesting invalid date handling...")

    invalid_date = "Not a valid date"
    assert parse_date_to_iso(invalid_date) == invalid_date

    print("  ✓ Invalid dates return original string")


def main():
    """Run all tests."""
    print("=== Testing date parsing functionality ===\n")

    test_parse_english_dates()
    test_parse_spanish_dates()
    test_parse_french_dates()
    test_parse_german_dates()
    test_parse_iso_dates()
    test_invalid_dates()

    print("\n=== All date parsing tests passed ===")


if __name__ == "__main__":
    main()
