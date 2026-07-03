"""
Tests for Telegram message formatting in telegram_bot.py
"""

import os
import sys

# Add parent directory to path to import telegram_bot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from telegram_bot import get_translation


def test_language_list_header_formatting():
    """
    Test that language_list_header is formatted with bold Markdown asterisks.

    The header should be wrapped in asterisks for Telegram Markdown bold formatting.
    Expected format: "*<text>*\n\n"
    """
    result = get_translation("en-us", "language_list_header")

    # Check that the result has the correct Markdown bold format structure
    assert result.startswith("*"), (
        f"Header should start with asterisk for bold, got: {repr(result)}"
    )
    assert result.endswith("*\n\n"), (
        f"Header should end with asterisk and two newlines, got: {repr(result)}"
    )

    # Verify it's not empty (has content between the asterisks)
    content = result[1:-3]  # Strip leading * and trailing *\n\n
    assert len(content) > 0, (
        f"Header should have content between asterisks, got: {repr(result)}"
    )

    print("✓ language_list_header is correctly formatted with bold asterisks")


def test_help_title_formatting():
    """
    Test that help_title is also formatted with bold Markdown asterisks.
    This is another header that should be bold.
    """
    result = get_translation("en-us", "help_title")

    # Check that the result has asterisks for bold formatting
    assert result.startswith("*"), (
        f"Help title should start with asterisk for bold, got: {repr(result)}"
    )
    assert result.endswith("*\n\n"), (
        f"Help title should end with asterisk and newlines, got: {repr(result)}"
    )

    # Check it contains the expected text
    assert "CrazyOnes - Help" in result, (
        f"Help title should contain 'CrazyOnes - Help', got: {repr(result)}"
    )

    print("✓ help_title is correctly formatted with bold asterisks")


def test_version_message_formatting():
    """
    Test that version_message is formatted with bold Markdown asterisks.

    Expected format: "*CrazyOnes v<version>*"
    """
    result = get_translation("en-us", "version_message", version="1.2.0")

    assert result.startswith("*"), (
        f"Version message should start with asterisk, got: {repr(result)}"
    )
    assert result.endswith("*"), (
        f"Version message should end with asterisk, got: {repr(result)}"
    )
    assert "1.2.0" in result, (
        f"Version message should contain the version, got: {repr(result)}"
    )
    assert "CrazyOnes" in result, (
        f"Version message should contain 'CrazyOnes', got: {repr(result)}"
    )

    print("✓ version_message is correctly formatted with bold asterisks")


def test_version_notification_header_formatting():
    """
    Test that version_notification_header is formatted with bold Markdown asterisks.

    Expected format: "*CrazyOnes v<version> ...*\n"
    """
    result = get_translation("en-us", "version_notification_header", version="1.2.0")

    assert result.startswith("*"), (
        f"Header should start with asterisk, got: {repr(result)}"
    )
    assert "*\n" in result, (
        f"Header should end with asterisk and newline, got: {repr(result)}"
    )
    assert "1.2.0" in result, f"Header should contain the version, got: {repr(result)}"

    print("✓ version_notification_header is correctly formatted")


def test_help_version_key_present():
    """Test that the help_version translation key exists for en-us."""
    result = get_translation("en-us", "help_version")

    assert result != "help_version", "help_version key should exist in translations"
    assert "/version" in result, (
        f"help_version should contain '/version', got: {repr(result)}"
    )

    print("✓ help_version key is present and contains '/version'")


def test_version_changes_key_present():
    """Test that version_changes key exists for English and Spanish locales."""
    en_result = get_translation("en-us", "version_changes")
    es_result = get_translation("es-es", "version_changes")

    assert en_result != "version_changes", "version_changes key should exist in en-us"
    assert es_result != "version_changes", "version_changes key should exist in es-es"

    # Spanish translation should differ from English
    assert en_result != es_result, "Spanish version_changes should differ from English"

    print("✓ version_changes keys are present for en-us and es-es")


if __name__ == "__main__":
    test_language_list_header_formatting()
    test_help_title_formatting()
    test_version_message_formatting()
    test_version_notification_header_formatting()
    test_help_version_key_present()
    test_version_changes_key_present()
    print("\nAll formatting tests passed!")
