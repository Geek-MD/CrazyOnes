#!/usr/bin/env python3
"""
Script to scrape Apple Updates page and extract language-specific URLs.

This script fetches the Apple Updates page and extracts all language-specific
URLs from the header, saving them to a JSON file. It also generates a mapping
of language codes to their display names.
"""

import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .utils import get_user_agent_headers

# Language code to name mapping
LANGUAGE_NAMES: dict[str, str] = {
    "en-us": "English/USA",
    "en-gb": "English/UK",
    "en-ca": "English/Canada",
    "en-au": "English/Australia",
    "es-es": "Español/España",
    "es-mx": "Español/México",
    "es-co": "Español/Colombia",
    "es-cl": "Español/Chile",
    "es-us": "Español/USA",
    "fr-fr": "Français/France",
    "fr-ca": "Français/Canada",
    "fr-sn": "Français/Sénégal",
    "de-de": "Deutsch/Deutschland",
    "it-it": "Italiano/Italia",
    "ja-jp": "日本語/日本",
    "ko-kr": "한국어/대한민국",
    "zh-cn": "简体中文/中国",
    "zh-tw": "繁體中文/台灣",
    "zh-hk": "繁體中文/香港",
    "pt-br": "Português/Brasil",
    "pt-pt": "Português/Portugal",
    "nl-nl": "Nederlands/Nederland",
    "ru-ru": "Русский/Россия",
    "pl-pl": "Polski/Polska",
    "ar-sa": "العربية/السعودية",
    "ar-ae": "العربية/الإمارات",
    "ar-eg": "العربية/مصر",
    "ar-kw": "العربية/الكويت",
    "ar-bh": "العربية/البحرين",
    "ar-jo": "العربية/الأردن",
    "ar-qa": "العربية/قطر",
    "he-il": "עברית/ישראל",
    "tr-tr": "Türkçe/Türkiye",
    "el-gr": "Ελληνικά/Ελλάδα",
    "hu-hu": "Magyar/Magyarország",
    "ro-ro": "Română/România",
    "fi-fi": "Suomi/Suomi",
    "no-no": "Norsk/Norge",
    "th-th": "ไทย/ประเทศไทย",
    "id-id": "Indonesia/Indonesia",
    "en-il": "English/Israel",
    "en-ae": "English/UAE",
    "en-sa": "English/Saudi Arabia",
    "en-hk": "English/Hong Kong",
    "en-al": "English/Albania",
    "en-is": "English/Iceland",
    "en-am": "English/Armenia",
    "en-az": "English/Azerbaijan",
    "en-jo": "English/Jordan",
    "en-bh": "English/Bahrain",
    "en-bn": "English/Brunei",
}


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
    headers = get_user_agent_headers()

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
    language_urls: dict[str, str], output_file: str = "data/language_urls.json"
) -> None:
    """
    Save language URLs to a JSON file.

    Args:
        language_urls: Dictionary mapping language codes to URLs
        output_file: Path to the output JSON file
    """
    # Create directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(language_urls, f, indent=2, ensure_ascii=False)

    print(f"Language URLs saved to {output_file}")
    print(f"Found {len(language_urls)} language versions:")
    for lang, url in sorted(language_urls.items()):
        print(f"  {lang}: {url}")


def load_language_names(
    names_file: str = "data/language_names.json",
) -> dict[str, str]:
    """
    Load language names from JSON file.

    Args:
        names_file: Path to the language names JSON file

    Returns:
        Dictionary mapping language codes to their display names
    """
    path = Path(names_file)
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_language_names(
    language_names: dict[str, str], names_file: str = "data/language_names.json"
) -> None:
    """
    Save language names to JSON file.

    Args:
        language_names: Dictionary mapping language codes to display names
        names_file: Path to the language names JSON file
    """
    # Create directory if it doesn't exist
    output_path = Path(names_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(names_file, "w", encoding="utf-8") as f:
        json.dump(language_names, f, indent=2, ensure_ascii=False, sort_keys=True)


def generate_language_names(language_codes: list[str]) -> dict[str, str]:
    """
    Generate language names mapping for given language codes.

    Args:
        language_codes: List of language codes

    Returns:
        Dictionary mapping language codes to display names
    """
    # Load existing language names
    existing_names = load_language_names()

    # Generate names for all language codes
    language_names: dict[str, str] = {}
    new_languages: list[str] = []

    for lang_code in language_codes:
        if lang_code in existing_names:
            # Use existing name
            language_names[lang_code] = existing_names[lang_code]
        elif lang_code in LANGUAGE_NAMES:
            # Use predefined name
            language_names[lang_code] = LANGUAGE_NAMES[lang_code]
            new_languages.append(lang_code)
        else:
            # Generate a basic name from the language code
            parts = lang_code.split("-")
            if len(parts) == 2:
                lang, country = parts
                language_names[lang_code] = f"{lang.upper()}/{country.upper()}"
            else:
                language_names[lang_code] = lang_code.upper()
            new_languages.append(lang_code)

    # Report new languages
    if new_languages:
        print(f"\nNew languages detected: {len(new_languages)}")
        for lang_code in new_languages:
            print(f"  ➕ {lang_code}: {language_names[lang_code]}")

    return language_names


def main() -> None:
    """Main function to orchestrate the scraping process."""
    apple_updates_url = "https://support.apple.com/en-us/100100"

    print(f"Fetching Apple Updates page: {apple_updates_url}\n")
    html_content = fetch_apple_updates_page(apple_updates_url)

    print("Extracting language-specific URLs...")
    language_urls = extract_language_urls(html_content, apple_updates_url)

    if not language_urls:
        print("Warning: No language URLs found. The page structure might have changed.")
        # Add the current URL as a fallback
        language_urls["en-us"] = apple_updates_url

    print()
    save_language_urls_to_json(language_urls)

    # Generate and save language names
    print("\nGenerating language names mapping...")
    language_names = generate_language_names(list(language_urls.keys()))
    save_language_names(language_names)
    print("Language names saved to data/language_names.json")
    print(f"Total languages: {len(language_names)}")


if __name__ == "__main__":
    main()
