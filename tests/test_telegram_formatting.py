"""
Tests for Telegram message formatting in telegram_bot.py
"""

import os
import sys

# Add parent directory to path to import telegram_bot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from telegram_bot import (
    format_update_line_markdown,
    format_update_message,
    format_update_number,
    get_translation,
    legacy_markdown_to_commonmark,
    render_telegram_markdown,
)


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


def test_help_version_formatting():
    """Test that /version command is not italicized in help output."""
    result = get_translation("en-us", "help_version")

    assert result.startswith("/version - "), (
        f"help_version should not be italicized, got: {repr(result)}"
    )

    print("✓ help_version command formatting is correct")


def test_version_changes_key_present():
    """Test that version_changes key exists for English and Spanish locales."""
    en_result = get_translation("en-us", "version_changes")
    es_result = get_translation("es-es", "version_changes")

    assert en_result != "version_changes", "version_changes key should exist in en-us"
    assert es_result != "version_changes", "version_changes key should exist in es-es"

    # Spanish translation should differ from English
    assert en_result != es_result, "Spanish version_changes should differ from English"

    print("✓ version_changes keys are present for en-us and es-es")


def test_updates_found_tag_keeps_blank_line_before_results():
    """The tag header must remain separated from the first numbered update."""
    result = get_translation(
        "es-cl",
        "updates_found_tag",
        display_name="Spanish/Chile",
        count=95,
        tag="mac",
        showing=10,
    )

    assert result.endswith("Mostrando las 10 más recientes:\n\n")


def test_update_numbers_are_bold_and_italic():
    """Every numbered update prefix includes its point in bold italics."""
    assert format_update_number(7) == "***7.***"

    item = {"name": "iOS 27.2", "target": "iPhone", "date": "2026-11-12"}
    expected_prefix = "*_7\\._* "
    assert render_telegram_markdown(
        format_update_message(item, 7, "es-cl")
    ).startswith(expected_prefix)
    assert render_telegram_markdown(
        format_update_message(item, 7, "en-us")
    ).startswith(expected_prefix)


def test_telegramify_markdown_escapes_content_and_preserves_links():
    """Apple text and URLs are rendered as valid Telegram MarkdownV2."""
    item = {
        "name": "iOS <Preview> & iPadOS",
        "target": "iPhone > 11 & later",
        "date": "2026-11-18",
        "url": 'https://example.test/update?a=1&label="beta"',
    }

    result = render_telegram_markdown(format_update_line_markdown(item, 1))

    assert result.startswith("*_1\\._* ")
    assert "iOS <Preview\\> & iPadOS" in result
    assert "iPhone \\> 11 & later" in result
    assert "a=1&label=%22beta%22" in result


def test_update_header_legacy_markdown_is_converted_to_commonmark():
    """Existing translated headers retain their formatting through telegramify."""
    header = "*CrazyOnes - Actualizaciones de Apple* - _Spanish/Chile_\n\n"

    commonmark = legacy_markdown_to_commonmark(header)
    assert commonmark == (
        "**CrazyOnes - Actualizaciones de Apple** - "
        "*Spanish/Chile*\n\n"
    )
    rendered = render_telegram_markdown(commonmark)
    assert rendered.startswith("*CrazyOnes \\- Actualizaciones de Apple*")


if __name__ == "__main__":
    test_language_list_header_formatting()
    test_help_title_formatting()
    test_version_message_formatting()
    test_version_notification_header_formatting()
    test_help_version_key_present()
    test_help_version_formatting()
    test_version_changes_key_present()
    print("\nAll formatting tests passed!")
