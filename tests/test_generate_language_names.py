#!/usr/bin/env python3
"""
Test script for the generate_language_names module.
"""

import json
import tempfile
from pathlib import Path

from scripts.generate_language_names import (
    generate_language_name,
    generate_language_names,
    load_language_urls,
    save_language_names,
    update_language_names,
)


def test_generate_language_name():
    """Test language name generation from code."""
    print("Testing language name generation...")

    # Test known languages
    assert generate_language_name("en-us") == "English/USA"
    assert generate_language_name("es-es") == "Spanish/Spain"
    assert generate_language_name("fr-fr") == "French/France"
    assert generate_language_name("ja-jp") == "Japanese/Japan"
    assert generate_language_name("zh-cn") == "Chinese/China"

    # Test unknown language (should generate from code)
    result = generate_language_name("xx-yy")
    assert result == "Xx/YY", f"Expected 'Xx/YY', got '{result}'"

    print("  ✓ Language name generation works correctly")


def test_generate_language_names():
    """Test generating names for multiple languages."""
    print("\nTesting multiple language names generation...")

    language_urls = {
        "en-us": "https://support.apple.com/en-us/100100",
        "es-es": "https://support.apple.com/es-es/100100",
        "fr-fr": "https://support.apple.com/fr-fr/100100",
    }

    names = generate_language_names(language_urls)

    assert len(names) == 3, f"Expected 3 names, got {len(names)}"
    assert names["en-us"] == "English/USA"
    assert names["es-es"] == "Spanish/Spain"
    assert names["fr-fr"] == "French/France"

    print("  ✓ Multiple language names generation works correctly")


def test_save_and_load():
    """Test saving and loading language names."""
    print("\nTesting save and load functionality...")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_names = {
            "en-us": "English/USA",
            "es-es": "Spanish/Spain",
            "fr-fr": "French/France",
        }

        output_file = Path(tmpdir) / "test_names.json"
        save_language_names(test_names, str(output_file))

        assert output_file.exists(), "Output file should exist"

        with open(output_file, encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == test_names, "Loaded data should match saved data"

    print("  ✓ Save and load functionality works correctly")


def test_update_language_names():
    """Test updating language names with new entries."""
    print("\nTesting update language names functionality...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test language URLs file
        urls_file = Path(tmpdir) / "language_urls.json"
        urls_data = {
            "en-us": "https://support.apple.com/en-us/100100",
            "es-es": "https://support.apple.com/es-es/100100",
            "fr-fr": "https://support.apple.com/fr-fr/100100",
        }
        with open(urls_file, "w", encoding="utf-8") as f:
            json.dump(urls_data, f)

        # Create existing language names file with partial data
        names_file = Path(tmpdir) / "language_names.json"
        existing_names = {
            "en-us": "English/USA",
        }
        with open(names_file, "w", encoding="utf-8") as f:
            json.dump(existing_names, f)

        # Update language names
        update_language_names(str(urls_file), str(names_file))

        # Load updated names
        with open(names_file, encoding="utf-8") as f:
            updated_names = json.load(f)

        # Should have all three languages now
        assert len(updated_names) == 3, f"Expected 3 names, got {len(updated_names)}"
        assert "en-us" in updated_names
        assert "es-es" in updated_names
        assert "fr-fr" in updated_names

    print("  ✓ Update language names functionality works correctly")


def test_update_language_names_no_existing_file():
    """Test updating language names when names file doesn't exist."""
    print("\nTesting update with no existing names file...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test language URLs file
        urls_file = Path(tmpdir) / "language_urls.json"
        urls_data = {
            "en-us": "https://support.apple.com/en-us/100100",
            "es-es": "https://support.apple.com/es-es/100100",
        }
        with open(urls_file, "w", encoding="utf-8") as f:
            json.dump(urls_data, f)

        # Names file doesn't exist yet
        names_file = Path(tmpdir) / "language_names.json"

        # Update language names (should create new file)
        update_language_names(str(urls_file), str(names_file))

        # Verify file was created
        assert names_file.exists(), "Names file should be created"

        # Load and verify content
        with open(names_file, encoding="utf-8") as f:
            updated_names = json.load(f)

        assert len(updated_names) == 2, f"Expected 2 names, got {len(updated_names)}"
        assert "en-us" in updated_names
        assert "es-es" in updated_names

    print("  ✓ Update with no existing file works correctly")


def test_load_missing_file():
    """Test error handling when language URLs file is missing."""
    print("\nTesting missing file error handling...")

    try:
        load_language_urls("nonexistent_file.json")
        raise AssertionError("Should raise FileNotFoundError")
    except FileNotFoundError as e:
        assert "not found" in str(e).lower()
        print("  ✓ Missing file error handling works correctly")


def main():
    """Run all tests."""
    print("=== Testing generate_language_names module ===\n")

    test_generate_language_name()
    test_generate_language_names()
    test_save_and_load()
    test_update_language_names()
    test_update_language_names_no_existing_file()
    test_load_missing_file()

    print("\n=== All tests passed ===")


if __name__ == "__main__":
    main()
