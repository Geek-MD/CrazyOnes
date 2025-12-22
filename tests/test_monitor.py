#!/usr/bin/env python3
"""
Test script for the monitor_apple_updates module.
"""

import json
import tempfile
from pathlib import Path

from scripts.monitor_apple_updates import (
    compute_content_hash,
    detect_changes,
    extract_security_updates_table,
    load_language_urls,
    load_tracking_data,
    save_tracking_data,
    save_updates_to_json,
)


def test_compute_content_hash():
    """Test content hash computation."""
    print("Testing content hash computation...")

    content1 = "This is test content"
    content2 = "This is test content"
    content3 = "This is different content"

    hash1 = compute_content_hash(content1)
    hash2 = compute_content_hash(content2)
    hash3 = compute_content_hash(content3)

    assert hash1 == hash2, "Same content should produce same hash"
    assert hash1 != hash3, "Different content should produce different hash"
    assert len(hash1) == 64, "SHA256 hash should be 64 characters"

    print("  ✓ Content hash computation works correctly")


def test_extract_security_updates_table():
    """Test security updates table extraction."""
    print("\nTesting security updates table extraction...")

    # Mock HTML with Apple security updates table structure
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Apple Security Updates</title></head>
    <body>
        <h2 class="gb-header">Apple security updates</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Available for</th>
                <th>Release date</th>
            </tr>
            <tr>
                <td><a href="/HT213530">iOS 17.2 and iPadOS 17.2</a></td>
                <td>
                    iPhone XS and later, iPad Pro 12.9-inch 2nd generation and later
                </td>
                <td>11 Dec 2023</td>
            </tr>
            <tr>
                <td><a href="/HT213531">macOS Sonoma 14.2</a></td>
                <td>macOS Sonoma</td>
                <td>11 Dec 2023</td>
            </tr>
            <tr>
                <td>watchOS 10.2</td>
                <td>Apple Watch Series 4 and later</td>
                <td>11 Dec 2023</td>
            </tr>
        </table>
    </body>
    </html>
    """

    base_url = "https://support.apple.com/en-us/100100"
    updates = extract_security_updates_table(mock_html, base_url)

    assert len(updates) == 3, f"Expected 3 updates, got {len(updates)}"

    # Check first update (with URL)
    assert updates[0]["id"] == 1, "First update should have id 1"
    assert updates[0]["name"] == "iOS 17.2 and iPadOS 17.2"
    assert updates[0]["url"] == "https://support.apple.com/HT213530"
    assert updates[0]["target"].startswith("iPhone XS")
    # Date should be in ISO format (YYYY-MM-DD)
    assert updates[0]["date"] == "2023-12-11"

    # Check second update (with URL)
    assert updates[1]["id"] == 2, "Second update should have id 2"
    assert updates[1]["name"] == "macOS Sonoma 14.2"
    assert updates[1]["url"] == "https://support.apple.com/HT213531"
    # Date should be in ISO format (YYYY-MM-DD)
    assert updates[1]["date"] == "2023-12-11"

    # Check third update (without URL)
    assert updates[2]["id"] == 3, "Third update should have id 3"
    assert updates[2]["name"] == "watchOS 10.2"
    assert "url" not in updates[2] or updates[2].get("url") is None
    # Date should be in ISO format (YYYY-MM-DD)
    assert updates[2]["date"] == "2023-12-11"

    print("  ✓ Security updates table extraction works correctly")
    print(f"    Extracted {len(updates)} updates with correct structure")
    print("  ✓ IDs are sequential (1, 2, 3)")
    print("  ✓ Dates are in ISO format (YYYY-MM-DD)")


def test_detect_changes():
    """Test change detection logic."""
    print("\nTesting change detection...")

    language_urls = {
        "en-us": "https://support.apple.com/en-us/100100",
        "es-es": "https://support.apple.com/es-es/100100",
        "fr-fr": "https://support.apple.com/fr-fr/100100",
    }

    # Test with empty tracking data (all should be changed)
    tracking_data = {}
    changed = detect_changes(language_urls, tracking_data)
    assert len(changed) == 3, "All languages should be new"

    # Test with existing tracking data (no changes)
    tracking_data = {
        "en-us": {"url": "https://support.apple.com/en-us/100100", "hash": "abc123"},
        "es-es": {"url": "https://support.apple.com/es-es/100100", "hash": "def456"},
        "fr-fr": {"url": "https://support.apple.com/fr-fr/100100", "hash": "ghi789"},
    }
    changed = detect_changes(language_urls, tracking_data)
    assert len(changed) == 0, "No languages should have changed"

    # Test with URL change
    tracking_data["en-us"]["url"] = "https://support.apple.com/en-us/999999"
    changed = detect_changes(language_urls, tracking_data)
    assert len(changed) == 1, "One language should have changed"
    assert "en-us" in changed, "en-us should be in changed list"

    # Test with new language
    language_urls["de-de"] = "https://support.apple.com/de-de/100100"
    changed = detect_changes(language_urls, tracking_data)
    assert "de-de" in changed, "New language should be detected"

    print("  ✓ Change detection works correctly")


def test_save_and_load_tracking_data():
    """Test saving and loading tracking data."""
    print("\nTesting tracking data save/load...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tracking_file = Path(tmpdir) / "test_tracking.json"

        tracking_data = {
            "en-us": {"url": "https://example.com/en-us", "hash": "abc123"},
            "es-es": {"url": "https://example.com/es-es", "hash": "def456"},
        }

        save_tracking_data(tracking_data, str(tracking_file))
        assert tracking_file.exists(), "Tracking file should be created"

        loaded_data = load_tracking_data(str(tracking_file))
        assert loaded_data == tracking_data, "Loaded data should match saved data"

    print("  ✓ Tracking data save/load works correctly")


def test_save_updates_to_json():
    """Test saving updates to JSON files."""
    print("\nTesting updates save to JSON...")

    with tempfile.TemporaryDirectory() as tmpdir:
        updates = [
            {
                "id": 1,
                "name": "iOS 17.2",
                "url": "https://support.apple.com/HT213530",
                "target": "iPhone XS and later",
                "date": "2023-12-11",
            },
            {
                "id": 2,
                "name": "macOS Sonoma 14.2",
                "url": "https://support.apple.com/HT213531",
                "target": "macOS Sonoma",
                "date": "2023-12-11",
            },
        ]

        save_updates_to_json(updates, "en-us", tmpdir)

        output_file = Path(tmpdir) / "en-us.json"
        assert output_file.exists(), "Output file should be created"

        with open(output_file, encoding="utf-8") as f:
            loaded_updates = json.load(f)

        assert loaded_updates == updates, "Loaded updates should match saved updates"
        assert len(loaded_updates) == 2, "Should have 2 updates"
        assert loaded_updates[0]["id"] == 1, "First update should have id 1"
        assert loaded_updates[1]["id"] == 2, "Second update should have id 2"

    print("  ✓ Updates save to JSON works correctly")


def test_extract_with_alternative_html():
    """Test extraction with alternative HTML structures."""
    print("\nTesting extraction with alternative HTML structures...")

    # Test with Spanish date format
    mock_html = """
    <html>
    <body>
        <h2 class="gb-header">Actualizaciones de seguridad de Apple</h2>
        <table>
            <tr><th>Nombre</th><th>Disponible para</th><th>Fecha</th></tr>
            <tr>
                <td><a href="/120306">watchOS 10.3</a></td>
                <td>Apple Watch Series 4 y posterior</td>
                <td>22 de enero de 2024</td>
            </tr>
            <tr>
                <td><a href="/120303">Actualización de firmware 2.0.6</a></td>
                <td>Magic Keyboard</td>
                <td>09 de enero de 2024</td>
            </tr>
        </table>
    </body>
    </html>
    """

    base_url = "https://support.apple.com/es-cl/100100"
    updates = extract_security_updates_table(mock_html, base_url)

    assert len(updates) == 2, f"Expected 2 updates, got {len(updates)}"

    # Check Spanish date parsing
    assert updates[0]["id"] == 1, "First update should have id 1"
    # Spanish date '22 de enero de 2024' should parse to 2024-01-22
    assert updates[0]["date"] == "2024-01-22"
    assert updates[1]["id"] == 2, "Second update should have id 2"
    # Spanish date '09 de enero de 2024' should parse to 2024-01-09
    assert updates[1]["date"] == "2024-01-09"

    print("  ✓ Alternative HTML structure handling tested")
    print("  ✓ Spanish date format parsed correctly to ISO format")


def test_load_language_urls_missing_file():
    """Test loading language URLs when file doesn't exist."""
    print("\nTesting missing language URLs file handling...")

    try:
        load_language_urls("nonexistent_file.json")
        raise AssertionError("Should raise FileNotFoundError")
    except FileNotFoundError as e:
        assert "not found" in str(e).lower()
        print("  ✓ Missing file handling works correctly")


def main():
    """Run all tests."""
    print("=== Testing monitor_apple_updates module ===\n")

    test_compute_content_hash()
    test_extract_security_updates_table()
    test_detect_changes()
    test_save_and_load_tracking_data()
    test_save_updates_to_json()
    test_extract_with_alternative_html()
    test_load_language_urls_missing_file()

    print("\n=== All tests passed ===")


if __name__ == "__main__":
    main()
