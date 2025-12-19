#!/usr/bin/env python3
"""
Test script to verify the language URL extraction logic works correctly.
"""

import json
from scrape_apple_updates import extract_language_urls, save_language_urls_to_json


def test_with_mock_html():
    """Test the extraction with a mock HTML page."""
    
    # Mock HTML that simulates Apple's page structure with language links
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="alternate" hreflang="en-us" href="https://support.apple.com/en-us/100100">
        <link rel="alternate" hreflang="es-es" href="https://support.apple.com/es-es/100100">
        <link rel="alternate" hreflang="fr-fr" href="https://support.apple.com/fr-fr/100100">
        <link rel="alternate" hreflang="de-de" href="https://support.apple.com/de-de/100100">
        <link rel="alternate" hreflang="it-it" href="https://support.apple.com/it-it/100100">
        <link rel="alternate" hreflang="ja-jp" href="https://support.apple.com/ja-jp/100100">
        <link rel="alternate" hreflang="zh-cn" href="https://support.apple.com/zh-cn/100100">
    </head>
    <body>
        <header>
            <nav>
                <a href="/en-us/100100" hreflang="en-us">English (US)</a>
                <a href="/es-es/100100" hreflang="es-es">Español</a>
                <a href="/fr-fr/100100" hreflang="fr-fr">Français</a>
            </nav>
        </header>
        <main>
            <h1>Apple Security Updates</h1>
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
        save_language_urls_to_json(language_urls, 'test_language_urls.json')
        
        # Verify JSON file was created
        with open('test_language_urls.json', 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            print(f"\nJSON file created successfully with {len(loaded_data)} entries")
            
        return True
    else:
        print("Error: No language URLs extracted")
        return False


if __name__ == '__main__':
    success = test_with_mock_html()
    if success:
        print("\n✓ Test passed: Language URL extraction is working correctly")
    else:
        print("\n✗ Test failed: Language URL extraction did not work")
        exit(1)
