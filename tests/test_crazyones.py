#!/usr/bin/env python3
"""
Test script for the crazyones main coordinator script.
"""

import json
import tempfile
from pathlib import Path

from crazyones import load_config, parse_arguments


def test_load_config():
    """Test loading configuration from JSON file."""
    print("Testing config loading...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test config file
        config_file = Path(tmpdir) / "test_config.json"
        test_config = {
            "apple_updates_url": "https://support.apple.com/en-us/100100"
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f)

        # Load config
        loaded_config = load_config(str(config_file))

        assert "apple_updates_url" in loaded_config
        assert loaded_config["apple_updates_url"] == test_config["apple_updates_url"]

    print("  ✓ Config loading works correctly")


def test_load_config_missing_file():
    """Test error handling when config file is missing."""
    print("\nTesting missing config file error handling...")

    try:
        load_config("nonexistent_config.json")
        raise AssertionError("Should raise FileNotFoundError")
    except FileNotFoundError as e:
        assert "not found" in str(e).lower()
        print("  ✓ Missing config file error handling works correctly")


def test_load_config_missing_field():
    """Test error handling when required field is missing."""
    print("\nTesting missing field error handling...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a config file without the required field
        config_file = Path(tmpdir) / "invalid_config.json"
        invalid_config = {"some_other_field": "value"}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(invalid_config, f)

        try:
            load_config(str(config_file))
            raise AssertionError("Should raise ValueError")
        except ValueError as e:
            assert "apple_updates_url" in str(e).lower()
            print("  ✓ Missing field error handling works correctly")


def test_parse_arguments_no_args():
    """Test parsing arguments when no arguments are provided."""
    print("\nTesting argument parsing with no arguments...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate no arguments
        sys.argv = ["crazyones.py"]
        args = parse_arguments()

        assert args.url is None, "URL should be None when not provided"

        print("  ✓ Argument parsing with no arguments works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_parse_arguments_with_url():
    """Test parsing arguments when URL is provided."""
    print("\nTesting argument parsing with URL argument...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate URL argument
        test_url = "https://support.apple.com/es-es/100100"
        sys.argv = ["crazyones.py", "--url", test_url]
        args = parse_arguments()

        assert args.url == test_url, f"URL should be {test_url}"

        print("  ✓ Argument parsing with URL works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_parse_arguments_with_short_url():
    """Test parsing arguments with short form -u."""
    print("\nTesting argument parsing with short form URL...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate short form URL argument
        test_url = "https://support.apple.com/fr-fr/100100"
        sys.argv = ["crazyones.py", "-u", test_url]
        args = parse_arguments()

        assert args.url == test_url, f"URL should be {test_url}"

        print("  ✓ Argument parsing with short form works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def main():
    """Run all tests."""
    print("=== Testing crazyones coordinator module ===\n")

    test_load_config()
    test_load_config_missing_file()
    test_load_config_missing_field()
    test_parse_arguments_no_args()
    test_parse_arguments_with_url()
    test_parse_arguments_with_short_url()

    print("\n=== All tests passed ===")


if __name__ == "__main__":
    main()
