#!/usr/bin/env python3
"""
Module to monitor changes in language_urls.json and scrape Apple security updates.

This module monitors the language_urls.json file created by scrape_apple_updates.py
and scrapes the security updates table from each language page. For each language,
it extracts the table data (name with URL, target, date) and saves it to individual
JSON files. It tracks content changes to avoid re-processing unchanged pages.
"""

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from .utils import get_user_agent_headers


def load_language_urls(file_path: str = "data/language_urls.json") -> dict[str, str]:
    """
    Load language URLs from JSON file.

    Args:
        file_path: Path to the language URLs JSON file

    Returns:
        Dictionary mapping language codes to URLs

    Raises:
        FileNotFoundError: If the language URLs file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Language URLs file not found: {file_path}")

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_tracking_data(
    tracking_file: str = "data/updates_tracking.json",
) -> dict[str, dict[str, str]]:
    """
    Load tracking data for language URLs and their content hashes.

    Args:
        tracking_file: Path to the tracking JSON file

    Returns:
        Dictionary with language codes as keys and tracking info (url, hash) as values
    """
    path = Path(tracking_file)
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_tracking_data(
    tracking_data: dict[str, dict[str, str]],
    tracking_file: str = "data/updates_tracking.json",
) -> None:
    """
    Save tracking data for language URLs and their content hashes.

    Args:
        tracking_data: Dictionary with language codes and tracking info
        tracking_file: Path to the tracking JSON file
    """
    with open(tracking_file, "w", encoding="utf-8") as f:
        json.dump(tracking_data, f, indent=2, ensure_ascii=False)


def compute_content_hash(content: str) -> str:
    """
    Compute SHA256 hash of content for change detection.

    Args:
        content: Content to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def fetch_page_content(url: str) -> str:
    """
    Fetch page content with proper User-Agent.

    Args:
        url: URL to fetch

    Returns:
        HTML content of the page

    Raises:
        requests.RequestException: If the request fails
    """
    headers = get_user_agent_headers()

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.text


def extract_security_updates_table(
    html_content: str, base_url: str
) -> list[dict[str, Any]]:
    """
    Extract security updates table from HTML content.

    Looks for the table under <h2 class="gb-header">Apple security updates</h2>
    and extracts three columns: name (with URL if available), target, and date.

    Args:
        html_content: HTML content to parse
        base_url: Base URL for resolving relative links

    Returns:
        List of dictionaries with 'name', 'url', 'target', and 'date' keys
    """
    soup = BeautifulSoup(html_content, "lxml")
    updates: list[dict[str, Any]] = []

    # Find the h2 with class gb-header containing "Apple security updates"
    h2_elements = soup.find_all("h2", class_="gb-header")
    target_h2: Tag | None = None

    for h2 in h2_elements:
        if "Apple security updates" in h2.get_text():
            target_h2 = h2
            break

    if not target_h2:
        # Try alternative patterns - sometimes it might be different
        target_h2 = soup.find("h2", string=lambda s: s and "security" in s.lower())

    if not target_h2:
        return updates

    # Find the next table after this h2
    table = target_h2.find_next("table")
    if not table:
        return updates

    # Get all rows, skip the header row (first row with th elements)
    rows = table.find_all("tr")

    for row in rows:
        # Skip header rows (rows with th elements)
        if row.find("th"):
            continue

        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        # Extract data from the three columns
        # Column 0: Name (and URL if available)
        name_col = cols[0]
        name = name_col.get_text(strip=True)
        url = None
        link = name_col.find("a")
        if link and link.get("href"):
            url = link["href"]
            # Convert relative URLs to absolute
            if url and not url.startswith("http"):
                url = urljoin(base_url, url)

        # Column 1: Target
        target = cols[1].get_text(strip=True)

        # Column 2: Date
        date = cols[2].get_text(strip=True)

        if name:  # Only add if we have at least a name
            update_entry: dict[str, Any] = {
                "name": name,
                "target": target,
                "date": date,
            }
            if url:
                update_entry["url"] = url

            updates.append(update_entry)

    return updates


def save_updates_to_json(
    updates: list[dict[str, Any]], language_code: str, output_dir: str = "data/updates"
) -> None:
    """
    Save security updates to a JSON file for a specific language.

    Args:
        updates: List of security update dictionaries
        language_code: Language code (e.g., 'en-us', 'es-es')
        output_dir: Directory to save the JSON files
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    output_file = output_path / f"{language_code}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(updates, f, indent=2, ensure_ascii=False)


def detect_changes(
    language_urls: dict[str, str], tracking_data: dict[str, dict[str, str]]
) -> list[str]:
    """
    Detect which language URLs have changed or are new.

    Args:
        language_urls: Current language URLs mapping
        tracking_data: Previous tracking data

    Returns:
        List of language codes that need to be processed
    """
    changed_languages: list[str] = []

    for lang_code, url in language_urls.items():
        # Check if this is a new language or URL has changed
        if lang_code not in tracking_data:
            changed_languages.append(lang_code)
        elif tracking_data[lang_code].get("url") != url:
            changed_languages.append(lang_code)

    return changed_languages


def process_language_url(
    lang_code: str,
    url: str,
    tracking_data: dict[str, dict[str, str]],
    force_update: bool = False,
) -> bool:
    """
    Process a single language URL: fetch, parse, and save updates.

    Args:
        lang_code: Language code
        url: URL to process
        tracking_data: Current tracking data
        force_update: If True, process even if content hasn't changed

    Returns:
        True if processing was successful and updates were found
    """
    try:
        print(f"Processing {lang_code}: {url}")
        html_content = fetch_page_content(url)

        # Compute content hash for change detection
        content_hash = compute_content_hash(html_content)

        # Check if content has changed (unless force_update is True)
        if not force_update:
            if lang_code in tracking_data:
                if tracking_data[lang_code].get("hash") == content_hash:
                    print(f"  ⊙ No content changes detected for {lang_code}")
                    return False

        # Extract security updates
        updates = extract_security_updates_table(html_content, url)

        if updates:
            # Save to JSON file
            save_updates_to_json(updates, lang_code)
            print(f"  ✓ Saved {len(updates)} updates for {lang_code}")

            # Update tracking data
            tracking_data[lang_code] = {"url": url, "hash": content_hash}

            return True
        else:
            print(f"  ⚠ No updates found for {lang_code}")
            # Still update tracking data to avoid repeated attempts
            tracking_data[lang_code] = {"url": url, "hash": content_hash}
            return False

    except Exception as e:
        print(f"  ✗ Error processing {lang_code}: {e}")
        return False


def main() -> None:
    """Main function to orchestrate the monitoring and scraping process."""
    print("=== Apple Security Updates Monitor ===\n")

    # Load language URLs
    try:
        language_urls = load_language_urls()
        print(f"Loaded {len(language_urls)} language URLs\n")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(
            "Please run scrape_apple_updates.py first to generate "
            "data/language_urls.json"
        )
        return

    # Load tracking data
    tracking_data = load_tracking_data()

    # Determine which languages need processing
    if not tracking_data:
        # First run - process all languages
        print("First run detected - processing all language URLs\n")
        languages_to_process = list(language_urls.keys())
        force_update = True
    else:
        # Subsequent runs - only process changed URLs
        print("Checking for changes...\n")
        languages_to_process = detect_changes(language_urls, tracking_data)
        force_update = False

        if not languages_to_process:
            print("No changes detected in language URLs.")
            # Still check content changes for existing URLs
            languages_to_process = list(language_urls.keys())
            force_update = False

    # Process each language URL
    successful_count = 0
    for lang_code in languages_to_process:
        url = language_urls[lang_code]
        if process_language_url(lang_code, url, tracking_data, force_update):
            successful_count += 1

    # Save updated tracking data
    save_tracking_data(tracking_data)

    print("\n=== Summary ===")
    print(f"Processed: {len(languages_to_process)} languages")
    print(f"Successful: {successful_count} languages")
    print("Updates saved to 'data/updates/' directory")
    print("Tracking data saved to 'data/updates_tracking.json'")


if __name__ == "__main__":
    main()
