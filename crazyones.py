#!/usr/bin/env python3
"""
CrazyOnes - Main coordinator script for Apple Updates monitoring.

This is the main entry point for the CrazyOnes application. It orchestrates
the execution of various scripts to scrape and monitor Apple security updates.

Usage:
    python crazyones.py                    # Uses URL from config.json
    python crazyones.py --url <URL>        # Uses specified URL
    python crazyones.py -u <URL>           # Short form
"""

import argparse
import json
import sys
from pathlib import Path

from scripts.generate_language_names import update_language_names

# Import the main functions from our scripts
from scripts.scrape_apple_updates import (
    extract_language_urls,
    fetch_apple_updates_page,
    save_language_urls_to_json,
)


def load_config(config_file: str = "config.json") -> dict[str, str]:
    """
    Load configuration from JSON file.

    Args:
        config_file: Path to the config file

    Returns:
        Dictionary with configuration values

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is not valid JSON
    """
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}\n"
            f"Please create a config.json file with the following structure:\n"
            '{\n  "apple_updates_url": "https://support.apple.com/en-us/100100"\n}'
        )

    with open(config_path, encoding="utf-8") as f:
        config: dict[str, str] = json.load(f)

    # Validate required fields
    if "apple_updates_url" not in config:
        raise ValueError(
            'config.json must contain "apple_updates_url" field'
        )

    return config


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="CrazyOnes - Apple Updates monitoring coordinator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           Use URL from config.json
  %(prog)s --url https://support.apple.com/en-us/100100
  %(prog)s -u https://support.apple.com/es-es/100100
        """,
    )

    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="Apple Updates URL to scrape (overrides config.json)",
        metavar="URL",
    )

    return parser.parse_args()


def scrape_apple_updates(url: str) -> None:
    """
    Scrape Apple Updates page for language URLs.

    Args:
        url: The Apple Updates URL to scrape
    """
    print(f"Fetching Apple Updates page: {url}\n")

    try:
        html_content = fetch_apple_updates_page(url)
        print("Extracting language-specific URLs...")
        language_urls = extract_language_urls(html_content, url)

        if not language_urls:
            print(
                "Warning: No language URLs found. "
                "The page structure might have changed."
            )
            # Add the current URL as a fallback
            lang_code = url.split("/")[-2] if "/" in url else "en-us"
            language_urls[lang_code] = url

        print()
        save_language_urls_to_json(language_urls)

        # Generate/update language names dynamically
        print("\nUpdating language names...")
        update_language_names()

        print("\n✓ Apple Updates scraping completed successfully")

    except Exception as e:
        print(f"✗ Error during scraping: {e}")
        sys.exit(1)


def main() -> None:
    """Main function to orchestrate the CrazyOnes workflow."""
    print("=" * 60)
    print("CrazyOnes - Apple Updates Monitoring System")
    print("=" * 60)
    print()

    # Parse command line arguments
    args = parse_arguments()

    # Determine which URL to use
    if args.url:
        print(f"Using URL from command line argument: {args.url}")
        apple_updates_url = args.url
    else:
        print("Loading configuration from config.json...")
        try:
            config = load_config()
            apple_updates_url = config["apple_updates_url"]
            print(f"Using URL from config.json: {apple_updates_url}")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    print()
    print("-" * 60)
    print("Step 1: Scraping Apple Updates")
    print("-" * 60)
    print()

    # Execute the scraping process
    scrape_apple_updates(apple_updates_url)

    print()
    print("=" * 60)
    print("Workflow completed")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  - Language URLs saved to: data/language_urls.json")
    print("  - Language names saved to: data/language_names.json")
    print("  - You can now run: python -m scripts.monitor_apple_updates")
    print()


if __name__ == "__main__":
    main()
