#!/usr/bin/env python3
"""
CrazyOnes - Main coordinator script for Apple Updates monitoring.

This is the main entry point for the CrazyOnes application. It orchestrates
the execution of various scripts to scrape and monitor Apple security updates.

Usage:
    python crazyones.py -t <TOKEN>              # Uses URL from config.json
    python crazyones.py -t <TOKEN> -u <URL>     # Uses specified URL
    python crazyones.py --token <TOKEN> --url <URL>  # Long form
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from scripts.generate_language_names import update_language_names

# Import the main functions from our scripts
from scripts.scrape_apple_updates import (
    extract_language_urls,
    fetch_apple_updates_page,
    save_language_urls_to_json,
)

# Version from pyproject.toml
__version__ = "0.5.0"


def rotate_log_file(log_file: str = "crazyones.log", max_lines: int = 1000) -> None:
    """
    Rotate log file to keep only the most recent lines.

    Args:
        log_file: Path to the log file
        max_lines: Maximum number of lines to keep
    """
    log_path = Path(log_file)
    if not log_path.exists():
        return

    # Read all lines from the log file
    with open(log_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Keep only the last max_lines
    if len(lines) > max_lines:
        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(lines[-max_lines:])


def setup_logging(log_file: str = "crazyones.log") -> None:
    """
    Set up logging to both console and file.

    Args:
        log_file: Path to the log file
    """
    # Rotate log file before setting up logging
    rotate_log_file(log_file)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_formatter = logging.Formatter("%(message)s")

    # Set up file handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_and_print(message: str) -> None:
    """
    Log a message and print it to console.

    Args:
        message: Message to log and print
    """
    logging.info(message)


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
            f"Please create a config.json file or run the script with "
            f"--token and --url parameters"
        )

    with open(config_path, encoding="utf-8") as f:
        config: dict[str, str] = json.load(f)

    return config


def save_config(config: dict[str, str], config_file: str = "config.json") -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary to save
        config_file: Path to the config file
    """
    config_path = Path(config_file)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add newline at end of file


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
  %(prog)s -t YOUR_TOKEN
  %(prog)s --token YOUR_TOKEN --url https://support.apple.com/en-us/100100
  %(prog)s -t YOUR_TOKEN -u https://support.apple.com/es-es/100100
        """,
    )

    # Add version argument
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Add required token argument
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        required=True,
        help="Telegram bot token (required)",
        metavar="TOKEN",
    )

    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="Apple Updates URL to scrape (saves to config.json for future use)",
        metavar="URL",
    )

    return parser.parse_args()


def scrape_apple_updates(url: str) -> None:
    """
    Scrape Apple Updates page for language URLs.

    Args:
        url: The Apple Updates URL to scrape
    """
    log_and_print(f"Fetching Apple Updates page: {url}")
    log_and_print("")

    try:
        html_content = fetch_apple_updates_page(url)
        log_and_print("Extracting language-specific URLs...")
        language_urls = extract_language_urls(html_content, url)

        if not language_urls:
            log_and_print(
                "Warning: No language URLs found. "
                "The page structure might have changed."
            )
            # Add the current URL as a fallback
            lang_code = url.split("/")[-2] if "/" in url else "en-us"
            language_urls[lang_code] = url

        log_and_print("")
        save_language_urls_to_json(language_urls)

        # Generate/update language names dynamically
        log_and_print("\nUpdating language names...")
        update_language_names()

        log_and_print("\n✓ Apple Updates scraping completed successfully")

    except Exception as e:
        log_and_print(f"✗ Error during scraping: {e}")
        logging.exception("Full traceback:")
        sys.exit(1)


def main() -> None:
    """Main function to orchestrate the CrazyOnes workflow."""
    # Set up logging first
    setup_logging()

    log_and_print("=" * 60)
    log_and_print("CrazyOnes - Apple Updates Monitoring System")
    log_and_print("=" * 60)
    log_and_print("")

    # Parse command line arguments
    args = parse_arguments()

    # Save token and URL to config.json
    try:
        # Try to load existing config, or create new one
        try:
            config = load_config()
        except FileNotFoundError:
            config = {}

        # Update token in config
        config["telegram_bot_token"] = args.token
        log_and_print(f"Telegram bot token: {'*' * 20} (provided)")

        # Determine which URL to use and save it
        if args.url:
            log_and_print(f"Using URL from command line argument: {args.url}")
            apple_updates_url = args.url
            config["apple_updates_url"] = apple_updates_url
        else:
            # Use URL from config if available, otherwise use default
            if "apple_updates_url" in config:
                apple_updates_url = config["apple_updates_url"]
                log_and_print(f"Using URL from config.json: {apple_updates_url}")
            else:
                msg = "Error: No URL specified and no default URL in config.json"
                log_and_print(msg)
                log_and_print("Please provide a URL with --url or -u")
                sys.exit(1)

        # Save updated config
        save_config(config)
        log_and_print("✓ Token and configuration saved to config.json")

    except Exception as e:
        log_and_print(f"⚠ Warning: Could not save to config.json: {e}")
        # Continue with provided values even if save fails
        apple_updates_url = args.url if args.url else ""
        if not apple_updates_url:
            log_and_print("Error: No URL available")
            sys.exit(1)

    log_and_print("")
    log_and_print("-" * 60)
    log_and_print("Step 1: Scraping Apple Updates")
    log_and_print("-" * 60)
    log_and_print("")

    # Execute the scraping process
    scrape_apple_updates(apple_updates_url)

    log_and_print("")
    log_and_print("=" * 60)
    log_and_print("Workflow completed")
    log_and_print("=" * 60)
    log_and_print("")
    log_and_print("Next steps:")
    log_and_print("  - Language URLs saved to: data/language_urls.json")
    log_and_print("  - Language names saved to: data/language_names.json")
    log_and_print("  - You can now run: python -m scripts.monitor_apple_updates")
    log_and_print("")


if __name__ == "__main__":
    main()
