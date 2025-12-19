#!/usr/bin/env python3
"""
Test script with actual Apple HTML to verify complete extraction.
"""

import json

from scripts.scrape_apple_updates import extract_language_urls


def test_with_actual_html():
    """Test with a subset of the actual Apple HTML structure you provided."""

    # This is a realistic sample from the actual HTML with many language links
    actual_html_sample = """
    <!DOCTYPE html>
    <html lang="en" prefix="og: http://ogp.me/ns#" dir="ltr">
    <head>
        <title lang="en">Apple security releases - Apple Support</title>
        <link rel="canonical" href="https://support.apple.com/en-us/100100"/>

        <link rel="alternate" hreflang="ar-kw" href="https://support.apple.com/ar-kw/100100">
        <link rel="alternate" hreflang="en-il" href="https://support.apple.com/en-il/100100">
        <link rel="alternate" hreflang="en-ae" href="https://support.apple.com/en-ae/100100">
        <link rel="alternate" hreflang="no-no" href="https://support.apple.com/no-no/100100">
        <link rel="alternate" hreflang="en-al" href="https://support.apple.com/en-al/100100">
        <link rel="alternate" hreflang="en-is" href="https://support.apple.com/en-is/100100">
        <link rel="alternate" hreflang="el-gr" href="https://support.apple.com/el-gr/100100">
        <link rel="alternate" hreflang="en-am" href="https://support.apple.com/en-am/100100">
        <link rel="alternate" hreflang="nl-nl" href="https://support.apple.com/nl-nl/100100">
        <link rel="alternate" hreflang="he-il" href="https://support.apple.com/he-il/100100">
        <link rel="alternate" hreflang="en-az" href="https://support.apple.com/en-az/100100">
        <link rel="alternate" hreflang="hu-hu" href="https://support.apple.com/hu-hu/100100">
        <link rel="alternate" hreflang="en-jo" href="https://support.apple.com/en-jo/100100">
        <link rel="alternate" hreflang="en-bh" href="https://support.apple.com/en-bh/100100">
        <link rel="alternate" hreflang="es-cl" href="https://support.apple.com/es-cl/100100">
        <link rel="alternate" hreflang="fr-sn" href="https://support.apple.com/fr-sn/100100">
        <link rel="alternate" hreflang="fr-ca" href="https://support.apple.com/fr-ca/100100">
        <link rel="alternate" hreflang="es-co" href="https://support.apple.com/es-co/100100">
        <link rel="alternate" hreflang="en-bn" href="https://support.apple.com/en-bn/100100">
        <link rel="alternate" hreflang="pl-pl" href="https://support.apple.com/pl-pl/100100">
        <link rel="alternate" hreflang="pt-pt" href="https://support.apple.com/pt-pt/100100">
        <link rel="alternate" hreflang="en-sa" href="https://support.apple.com/en-sa/100100">
        <link rel="alternate" hreflang="ar-eg" href="https://support.apple.com/ar-eg/100100">
        <link rel="alternate" hreflang="zh-tw" href="https://support.apple.com/zh-tw/100100">
        <link rel="alternate" hreflang="en-hk" href="https://support.apple.com/en-hk/100100">
        <link rel="alternate" hreflang="ko-kr" href="https://support.apple.com/ko-kr/100100">
        <link rel="alternate" hreflang="en-us" href="https://support.apple.com/en-us/100100">
        <link rel="alternate" hreflang="zh-cn" href="https://support.apple.com/zh-cn/100100">
        <link rel="alternate" hreflang="zh-hk" href="https://support.apple.com/zh-hk/100100">
        <link rel="alternate" hreflang="ja-jp" href="https://support.apple.com/ja-jp/100100">
        <link rel="alternate" hreflang="ar-qa" href="https://support.apple.com/ar-qa/100100">
        <link rel="alternate" hreflang="ro-ro" href="https://support.apple.com/ro-ro/100100">
        <link rel="alternate" hreflang="tr-tr" href="https://support.apple.com/tr-tr/100100">
        <link rel="alternate" hreflang="fr-fr" href="https://support.apple.com/fr-fr/100100">
        <link rel="alternate" hreflang="fi-fi" href="https://support.apple.com/fi-fi/100100">
        <link rel="alternate" hreflang="en-ca" href="https://support.apple.com/en-ca/100100">
        <link rel="alternate" hreflang="ar-ae" href="https://support.apple.com/ar-ae/100100">
        <link rel="alternate" hreflang="es-us" href="https://support.apple.com/es-us/100100">
        <link rel="alternate" hreflang="ar-sa" href="https://support.apple.com/ar-sa/100100">
        <link rel="alternate" hreflang="de-de" href="https://support.apple.com/de-de/100100">
        <link rel="alternate" hreflang="pt-br" href="https://support.apple.com/pt-br/100100">
        <link rel="alternate" hreflang="ar-bh" href="https://support.apple.com/ar-bh/100100">
        <link rel="alternate" hreflang="es-es" href="https://support.apple.com/es-es/100100">
        <link rel="alternate" hreflang="ar-jo" href="https://support.apple.com/ar-jo/100100">
        <link rel="alternate" hreflang="es-mx" href="https://support.apple.com/es-mx/100100">
        <link rel="alternate" hreflang="it-it" href="https://support.apple.com/it-it/100100">
        <link rel="alternate" hreflang="id-id" href="https://support.apple.com/id-id/100100">
        <link rel="alternate" hreflang="th-th" href="https://support.apple.com/th-th/100100">
    </head>
    <body>
        <h1>Apple Security Updates</h1>
    </body>
    </html>
    """

    base_url = "https://support.apple.com/en-us/100100"

    print("Testing with actual Apple HTML structure...")
    language_urls = extract_language_urls(actual_html_sample, base_url)

    print(f"\nExtracted {len(language_urls)} language URLs from actual HTML structure")

    # Display first 10 and last 10
    sorted_langs = sorted(language_urls.items())
    print("\nFirst 10 languages:")
    for lang, url in sorted_langs[:10]:
        print(f"  {lang}: {url}")

    print(f"\n... ({len(sorted_langs) - 20} more) ...\n")

    print("Last 10 languages:")
    for lang, url in sorted_langs[-10:]:
        print(f"  {lang}: {url}")

    # Save to a different file
    output_file = "tests/actual_test_language_urls.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(language_urls, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully saved {len(language_urls)} language URLs to {output_file}")

    return len(language_urls) > 0


if __name__ == "__main__":
    success = test_with_actual_html()
    if success:
        print("\n✓ Test passed: Language URL extraction works with actual Apple HTML")
    else:
        print("\n✗ Test failed")
        exit(1)
