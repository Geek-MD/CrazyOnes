"""
Tests for Telegram message formatting in telegram_bot.py
"""
import sys
import os

# Add parent directory to path to import telegram_bot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from telegram_bot import get_translation


def test_language_list_header_formatting():
    """
    Test that language_list_header is formatted with bold Markdown asterisks.
    
    The header should be wrapped in asterisks for Telegram Markdown bold formatting.
    Expected format: "*<text>*\n\n"
    """
    result = get_translation('en-us', 'language_list_header')
    
    # Check that the result has the correct Markdown bold format structure
    assert result.startswith('*'), f"Header should start with asterisk for bold, got: {repr(result)}"
    assert result.endswith('*\n\n'), f"Header should end with asterisk and two newlines, got: {repr(result)}"
    
    # Verify it's not empty (has content between the asterisks)
    content = result[1:-3]  # Strip leading * and trailing *\n\n
    assert len(content) > 0, f"Header should have content between asterisks, got: {repr(result)}"
    
    print("✓ language_list_header is correctly formatted with bold asterisks")


def test_help_title_formatting():
    """
    Test that help_title is also formatted with bold Markdown asterisks.
    This is another header that should be bold.
    """
    result = get_translation('en-us', 'help_title')
    
    # Check that the result has asterisks for bold formatting
    assert result.startswith('*'), f"Help title should start with asterisk for bold, got: {repr(result)}"
    assert result.endswith('*\n\n'), f"Help title should end with asterisk and newlines, got: {repr(result)}"
    
    # Check it contains the expected text
    assert 'CrazyOnes - Help' in result, f"Help title should contain 'CrazyOnes - Help', got: {repr(result)}"
    
    print("✓ help_title is correctly formatted with bold asterisks")


if __name__ == '__main__':
    test_language_list_header_formatting()
    test_help_title_formatting()
    print("\nAll formatting tests passed!")
