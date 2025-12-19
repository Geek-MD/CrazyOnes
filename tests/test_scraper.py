#!/usr/bin/env python3
"""
Test script to verify the language URL extraction logic works correctly.
"""

import json

from scripts.scrape_apple_updates import (
    extract_language_urls,
    save_language_urls_to_json,
)


def test_with_mock_html():
    """Test extraction with a mock HTML that matches Apple's structure."""

    # Mock HTML that simulates Apple's actual page structure with link tags in head
    mock_html = """
    <!DOCTYPE html>
    <html lang="en" prefix="og: http://ogp.me/ns#" dir="ltr">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <title lang="en">Apple security releases - Apple Support</title>
        <link rel="canonical" href="https://support.apple.com/en-us/100100"/>

        <link rel="alternate" hreflang="en-us" href="https://support.apple.com/en-us/100100">
        <link rel="alternate" hreflang="es-es" href="https://support.apple.com/es-es/100100">
        <link rel="alternate" hreflang="fr-fr" href="https://support.apple.com/fr-fr/100100">
        <link rel="alternate" hreflang="de-de" href="https://support.apple.com/de-de/100100">
        <link rel="alternate" hreflang="it-it" href="https://support.apple.com/it-it/100100">
        <link rel="alternate" hreflang="ja-jp" href="https://support.apple.com/ja-jp/100100">
        <link rel="alternate" hreflang="zh-cn" href="https://support.apple.com/zh-cn/100100">
        <link rel="alternate" hreflang="pt-br" href="https://support.apple.com/pt-br/100100">
        <link rel="alternate" hreflang="ko-kr" href="https://support.apple.com/ko-kr/100100">
        <link rel="alternate" hreflang="nl-nl" href="https://support.apple.com/nl-nl/100100">
        <link rel="alternate" hreflang="ru-ru" href="https://support.apple.com/ru-ru/100100">
        <link rel="alternate" hreflang="ar-sa" href="https://support.apple.com/ar-sa/100100">
    </head>
    <body>
        <header>
            <nav>
                <h1>Apple Security Updates</h1>
            </nav>
        </header>
        <main>
            <h2>Apple security releases</h2>
            <p>This document lists security updates for Apple software.</p>
        </main>
    </body>
    </html>
    """

    base_url = "https://support.apple.com/en-us/100100"

    print("Testing language URL extraction with mock HTML...")
    language_urls = extract_language_urls(mock_html, base_url)

    if language_urls:
        print(f"\nSuccessfully extracted {len(language_urls)} language URLs:")
        for lang, url in sorted(language_urls.items()):
            print(f"  {lang}: {url}")

        # Save to JSON
        save_language_urls_to_json(language_urls, "tests/test_language_urls.json")

        # Verify JSON file was created
        with open("tests/test_language_urls.json", encoding="utf-8") as f:
            loaded_data = json.load(f)
            print(f"\nJSON file created successfully with {len(loaded_data)} entries")

        return True
    else:
        print("Error: No language URLs extracted")
        return False


if __name__ == "__main__":
    success = test_with_mock_html()
    if success:
        print("\n✓ Test passed: Language URL extraction is working correctly")
    else:
        print("\n✗ Test failed: Language URL extraction did not work")
        exit(1)
