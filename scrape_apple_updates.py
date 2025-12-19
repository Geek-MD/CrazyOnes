#!/usr/bin/env python3
"""
Script to scrape Apple Updates page and extract language-specific URLs.

This script fetches the Apple Updates page and extracts all language-specific
URLs from the header, saving them to a JSON file.
"""

import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def fetch_apple_updates_page(url: str) -> str:
    """
    Fetch the Apple Updates page with proper User-Agent to avoid blocking.

    Args:
        url: The URL of the Apple Updates page

    Returns:
        The HTML content of the page

    Raises:
        requests.RequestException: If the request fails
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.text


def extract_language_urls(html_content: str, base_url: str) -> dict[str, str]:
    """
    Extract language-specific URLs from the HTML header.

    Args:
        html_content: The HTML content to parse
        base_url: The base URL to resolve relative URLs

    Returns:
        Dictionary mapping language codes to their URLs
    """
    soup = BeautifulSoup(html_content, "lxml")
    language_urls: dict[str, str] = {}

    # Apple uses <link rel="alternate" hreflang="xx-yy"> tags in the head section
    # These contain all the language-specific URLs
    for link_tag in soup.find_all("link", rel="alternate"):
        if link_tag.get("hreflang") and link_tag.get("href"):
            lang_code = link_tag["hreflang"]
            url = link_tag["href"]
            # Convert relative URLs to absolute if needed
            if not url.startswith("http"):
                url = urljoin(base_url, url)
            language_urls[lang_code] = url

    return language_urls


def save_language_urls_to_json(
    language_urls: dict[str, str], output_file: str = "language_urls.json"
) -> None:
    """
    Save language URLs to a JSON file.

    Args:
        language_urls: Dictionary mapping language codes to URLs
        output_file: Path to the output JSON file
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(language_urls, f, indent=2, ensure_ascii=False)

    print(f"Language URLs saved to {output_file}")
    print(f"Found {len(language_urls)} language versions:")
    for lang, url in sorted(language_urls.items()):
        print(f"  {lang}: {url}")


def main() -> None:
    """Main function to orchestrate the scraping process."""
    apple_updates_url = "https://support.apple.com/en-us/100100"

    print(f"Fetching Apple Updates page: {apple_updates_url}")
    html_content = fetch_apple_updates_page(apple_updates_url)

    print("Extracting language-specific URLs...")
    language_urls = extract_language_urls(html_content, apple_updates_url)

    if not language_urls:
        print("Warning: No language URLs found. The page structure might have changed.")
        # Add the current URL as a fallback
        language_urls["en-us"] = apple_updates_url

    save_language_urls_to_json(language_urls)


if __name__ == "__main__":
    main()
