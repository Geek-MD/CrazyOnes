#!/usr/bin/env python3
"""
Test script for the crazyones main coordinator script.
"""

import json
import tempfile
from pathlib import Path

from crazyones import (
    generate_systemd_service_content,
    load_config,
    parse_arguments,
    rotate_log_file,
    save_config,
    validate_telegram_token,
)


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


def test_parse_arguments_no_args():
    """Test parsing arguments when no arguments are provided."""
    print("\nTesting argument parsing with no arguments...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate no arguments (should succeed now, as config wizard will run)
        sys.argv = ["crazyones.py"]
        args = parse_arguments()

        # With no arguments, token should be None and config should be False
        assert args.token is None, "Token should be None when no arguments provided"
        assert args.config is False, "Config should be False when no arguments provided"

        print("  ✓ Argument parsing with no arguments works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_parse_arguments_with_token():
    """Test parsing arguments with only token provided."""
    print("\nTesting argument parsing with token only...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate token argument
        test_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        sys.argv = ["crazyones.py", "--token", test_token]
        args = parse_arguments()

        assert args.token == test_token, f"Token should be {test_token}"
        assert args.url is None, "URL should be None when not provided"

        print("  ✓ Argument parsing with token works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_parse_arguments_with_url():
    """Test parsing arguments when URL is provided."""
    print("\nTesting argument parsing with token and URL...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate token and URL arguments
        test_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        test_url = "https://support.apple.com/es-es/100100"
        sys.argv = ["crazyones.py", "--token", test_token, "--url", test_url]
        args = parse_arguments()

        assert args.token == test_token, f"Token should be {test_token}"
        assert args.url == test_url, f"URL should be {test_url}"

        print("  ✓ Argument parsing with token and URL works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_parse_arguments_with_short_url():
    """Test parsing arguments with short form -u and -t."""
    print("\nTesting argument parsing with short form...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate short form token and URL arguments
        test_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        test_url = "https://support.apple.com/fr-fr/100100"
        sys.argv = ["crazyones.py", "-t", test_token, "-u", test_url]
        args = parse_arguments()

        assert args.token == test_token, f"Token should be {test_token}"
        assert args.url == test_url, f"URL should be {test_url}"

        print("  ✓ Argument parsing with short form works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_save_config():
    """Test saving configuration to JSON file."""
    print("\nTesting config saving...")

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.json"
        test_config = {
            "apple_updates_url": "https://support.apple.com/es-es/100100"
        }

        # Save config
        save_config(test_config, str(config_file))

        # Verify file exists
        assert config_file.exists(), "Config file should be created"

        # Load and verify content
        with open(config_file, encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == test_config, "Saved config should match original"

    print("  ✓ Config saving works correctly")


def test_save_config_updates_existing():
    """Test updating an existing config file."""
    print("\nTesting config update...")

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.json"

        # Create initial config
        initial_config = {
            "apple_updates_url": "https://support.apple.com/en-us/100100"
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(initial_config, f)

        # Update config with new URL
        updated_config = {
            "apple_updates_url": "https://support.apple.com/es-es/100100"
        }
        save_config(updated_config, str(config_file))

        # Load and verify
        loaded = load_config(str(config_file))
        assert loaded["apple_updates_url"] == updated_config["apple_updates_url"]
        assert loaded["apple_updates_url"] != initial_config["apple_updates_url"]

    print("  ✓ Config update works correctly")


def test_rotate_log_file():
    """Test log file rotation."""
    print("\nTesting log file rotation...")

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        # Create a log file with more than max_lines
        lines = [f"Line {i}\n" for i in range(1500)]
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # Rotate to keep only 1000 lines
        rotate_log_file(str(log_file), max_lines=1000)

        # Verify only 1000 lines remain
        with open(log_file, encoding="utf-8") as f:
            remaining_lines = f.readlines()

        expected = 1000
        got = len(remaining_lines)
        assert got == expected, f"Expected {expected} lines, got {got}"
        # Check that we kept the last 1000 lines (500-1499)
        assert remaining_lines[0].strip() == "Line 500"
        assert remaining_lines[-1].strip() == "Line 1499"

    print("  ✓ Log file rotation works correctly")


def test_rotate_log_file_no_rotation_needed():
    """Test log file rotation when file has fewer lines than max."""
    print("\nTesting log rotation with small file...")

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        # Create a log file with fewer than max_lines
        lines = [f"Line {i}\n" for i in range(100)]
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # Rotate (should not change the file)
        rotate_log_file(str(log_file), max_lines=1000)

        # Verify all lines remain
        with open(log_file, encoding="utf-8") as f:
            remaining_lines = f.readlines()

        expected = 100
        got = len(remaining_lines)
        assert got == expected, f"Expected {expected} lines, got {got}"

    print("  ✓ Log rotation with small file works correctly")


def test_rotate_log_file_nonexistent():
    """Test log file rotation when file doesn't exist."""
    print("\nTesting log rotation with nonexistent file...")

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "nonexistent.log"

        # Should not raise an error
        rotate_log_file(str(log_file), max_lines=1000)

    print("  ✓ Log rotation with nonexistent file works correctly")


def test_validate_telegram_token():
    """Test Telegram token validation."""
    print("\nTesting Telegram token validation...")

    # Valid tokens
    valid_tokens = [
        "123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890",
        "1234567890:ABC-DEF_GHI123456789012345678901234",
        "12345678:abcdefghijklmnopqrstuvwxyz123456789",
    ]

    for token in valid_tokens:
        assert validate_telegram_token(token), f"Token should be valid: {token}"

    # Invalid tokens
    invalid_tokens = [
        "invalid_token",  # No colon separator
        "123:short",  # bot_id too short, auth_token too short
        "1234567:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890",  # bot_id too short
        "12345678901:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890",  # bot_id too long
        "123456789:short",  # auth_token too short
        "123456789:ABC def@#$%^&*()",  # invalid characters with spaces
        "123456789:ABC@def",  # invalid character @
        "",  # empty string
        "123456789:",  # missing auth_token
        ":ABCdefGHIjklMNOpqrsTUVwxyz-1234567890",  # missing bot_id
    ]

    for token in invalid_tokens:
        assert not validate_telegram_token(
            token
        ), f"Token should be invalid: {token}"

    print("  ✓ Telegram token validation works correctly")


def test_parse_arguments_with_config():
    """Test parsing arguments with --config flag."""
    print("\nTesting argument parsing with --config flag...")

    import sys

    # Save original argv
    original_argv = sys.argv

    try:
        # Simulate --config argument
        sys.argv = ["crazyones.py", "--config"]
        args = parse_arguments()

        assert args.config is True, "config flag should be True"
        assert args.token is None, "Token should be None when using --config"

        print("  ✓ Argument parsing with --config works correctly")
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_generate_systemd_service_content():
    """Test systemd service file content generation."""
    print("\nTesting systemd service file generation...")

    content = generate_systemd_service_content(
        python_path="/usr/bin/python3",
        script_path="/home/user/crazyones.py",
        work_dir="/home/user",
        user="testuser",
    )

    # Check that the content contains expected sections
    assert "[Unit]" in content, "Service file should have [Unit] section"
    assert "[Service]" in content, "Service file should have [Service] section"
    assert "[Install]" in content, "Service file should have [Install] section"

    # Check specific content
    assert "Description=CrazyOnes" in content
    expected_exec = (
        "ExecStart=/usr/bin/python3 /home/user/crazyones.py "
        "--daemon --interval 43200"
    )
    assert expected_exec in content
    assert "User=testuser" in content
    assert "WorkingDirectory=/home/user" in content
    assert "Restart=always" in content
    assert "WantedBy=multi-user.target" in content

    print("  ✓ Systemd service file generation works correctly")


def main():
    """Run all tests."""
    print("=== Testing crazyones coordinator module ===\n")

    test_load_config()
    test_load_config_missing_file()
    test_save_config()
    test_save_config_updates_existing()
    test_rotate_log_file()
    test_rotate_log_file_no_rotation_needed()
    test_rotate_log_file_nonexistent()
    test_validate_telegram_token()
    test_parse_arguments_no_args()
    test_parse_arguments_with_token()
    test_parse_arguments_with_url()
    test_parse_arguments_with_short_url()
    test_parse_arguments_with_config()
    test_generate_systemd_service_content()

    print("\n=== All tests passed ===")


if __name__ == "__main__":
    main()
