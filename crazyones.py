#!/usr/bin/env python3
"""
CrazyOnes - Main coordinator script for Apple Updates monitoring.

This is the main entry point for the CrazyOnes application. It orchestrates
the execution of various scripts to scrape and monitor Apple security updates.

Usage:
    python crazyones.py -t <TOKEN>              # One-time execution
    python crazyones.py -t <TOKEN> -u <URL>     # One-time with custom URL
    python crazyones.py -t <TOKEN> --daemon     # Run as daemon (checks 2x per day)
    python crazyones.py -t <TOKEN> --interval 3600  # Run every hour (custom)
"""

import argparse
import json
import logging
import re
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.generate_language_names import update_language_names

# Import the main functions from our scripts
from scripts.scrape_apple_updates import (
    extract_language_urls,
    fetch_apple_updates_page,
    save_language_urls_to_json,
)

# Version from pyproject.toml
__version__ = "0.6.0"

# Global flag for graceful shutdown
_shutdown_requested = False


def signal_handler(signum: int, frame: object) -> None:
    """
    Handle shutdown signals gracefully.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global _shutdown_requested
    _shutdown_requested = True
    log_and_print("\n\nShutdown signal received. Finishing current cycle...")


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

    # Custom formatter class for timezone-aware logging
    class TZFormatter(logging.Formatter):
        """Custom formatter with timezone in YYYY/MM/DD HH:MM:SS TZ format."""

        def formatTime(  # noqa: N802
            self, record: logging.LogRecord, datefmt: str | None = None
        ) -> str:
            """Format time with timezone in YYYY/MM/DD HH:MM:SS TZ format."""
            # Get current time with timezone
            dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
            # Get local timezone offset
            local_dt = datetime.fromtimestamp(record.created)
            offset = local_dt.astimezone().strftime('%z')
            # Format: YYYY/MM/DD HH:MM:SS +HHMM
            formatted_offset = f"{offset[:3]}:{offset[3:]}"
            return f"{dt.strftime('%Y/%m/%d %H:%M:%S')} {formatted_offset}"

    # Create formatters with custom timezone format
    file_formatter = TZFormatter("%(asctime)s - %(levelname)s - %(message)s")
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


def log_only(message: str, level: str = "ERROR") -> None:
    """
    Log a message only to file, not to console.

    Args:
        message: Message to log
        level: Log level (ERROR, WARNING, INFO, DEBUG)
    """
    # Get the logger and temporarily remove console handler
    logger = logging.getLogger()
    console_handlers = [
        h for h in logger.handlers
        if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout
    ]

    # Temporarily remove console handlers
    for handler in console_handlers:
        logger.removeHandler(handler)

    # Log the message
    if level == "ERROR":
        logging.error(message)
    elif level == "WARNING":
        logging.warning(message)
    elif level == "INFO":
        logging.info(message)
    else:
        logging.debug(message)

    # Restore console handlers
    for handler in console_handlers:
        logger.addHandler(handler)


def ask_token_confirmation(new_token: str, saved_token: str) -> bool:
    """
    Ask user to confirm if they want to use the new token.

    Args:
        new_token: The new token provided as parameter
        saved_token: The token saved in config.json

    Returns:
        True if user wants to use new token, False if they want to use saved token
    """
    print("\n" + "!" * 60)
    print("⚠ TOKEN MISMATCH DETECTED")
    print("!" * 60)
    print("\nThe token you provided is different from the saved token.")
    print(f"\nProvided token: {new_token[:10]}...{new_token[-10:]}")
    print(f"Saved token:    {saved_token[:10]}...{saved_token[-10:]}")
    print("\nWhat would you like to do?")
    print("  1. Use the NEW token (provided as parameter)")
    print("  2. Use the SAVED token (from config.json)")
    print()

    while True:
        try:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == "1":
                return True
            elif choice == "2":
                return False
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except (EOFError, KeyboardInterrupt):
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def validate_telegram_token(token: str) -> bool:
    """
    Validate Telegram bot token format using regex.

    Telegram bot tokens have the format: <bot_id>:<auth_token>
    - bot_id: 8-10 digits
    - auth_token: 35+ alphanumeric characters and hyphens/underscores

    Args:
        token: Telegram bot token to validate

    Returns:
        True if token format is valid, False otherwise

    Examples:
        >>> validate_telegram_token("123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890")
        True
        >>> validate_telegram_token("invalid_token")
        False
    """
    # Telegram bot token format: bot_id:auth_token
    # bot_id: 8-10 digits
    # auth_token: 35+ alphanumeric characters (can include - and _)
    pattern = r'^\d{8,10}:[A-Za-z0-9_-]{35,}$'
    return bool(re.match(pattern, token))


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


def get_version() -> str:
    """
    Get version from config.json or use default.

    Returns:
        Version string
    """
    try:
        config = load_config()
        return config.get("version", __version__)
    except (FileNotFoundError, json.JSONDecodeError):
        return __version__


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
  %(prog)s -t YOUR_TOKEN --daemon
  %(prog)s -t YOUR_TOKEN --interval 21600  # Check every 6 hours
        """,
    )

    # Add version argument - get version from config if available
    version = get_version()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
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

    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        help="Run as daemon (continuous monitoring with 12 hour interval, 2 times per day)",
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        help="Monitoring interval in seconds (implies daemon mode, default: 43200 = 12 hours)",
        metavar="SECONDS",
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
        raise


def run_monitoring_cycle(apple_updates_url: str) -> None:
    """
    Run a complete monitoring cycle: scrape and monitor updates.

    Args:
        apple_updates_url: The Apple Updates URL to scrape
    """
    log_and_print("-" * 60)
    log_and_print(f"Monitoring cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_and_print("-" * 60)
    log_and_print("")

    # Step 1: Scrape language URLs from Apple Updates page
    try:
        log_and_print("Step 1: Scraping Apple Updates page for language URLs...")
        scrape_apple_updates(apple_updates_url)
    except Exception as e:
        log_and_print(f"✗ Scraping failed: {e}")
        logging.exception("Full traceback:")
        return

    # Step 2: Monitor and scrape security updates from each language URL
    log_and_print("")
    log_and_print("Step 2: Monitoring security updates from language URLs...")
    log_and_print("")
    
    try:
        # Import monitor module
        from scripts.monitor_apple_updates import (
            load_language_urls,
            load_tracking_data,
            save_tracking_data,
            detect_changes,
            process_language_url,
        )
        
        # Load language URLs
        try:
            language_urls = load_language_urls()
            log_and_print(f"Loaded {len(language_urls)} language URLs")
        except FileNotFoundError as e:
            log_and_print(f"✗ Error: {e}")
            log_and_print("Language URLs file not found. Skipping security updates monitoring.")
            return

        # Load tracking data
        tracking_data = load_tracking_data()

        # Determine which languages need processing
        if not tracking_data:
            # First run - process all languages
            log_and_print("First run detected - processing all language URLs")
            log_and_print("")
            languages_to_process = list(language_urls.keys())
            force_update = True
        else:
            # Subsequent runs - check for changes
            log_and_print("Checking for changes...")
            log_and_print("")
            languages_to_process = detect_changes(language_urls, tracking_data)
            force_update = False

            if not languages_to_process:
                log_and_print("No URL changes detected. Checking content changes...")
                log_and_print("")
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

        log_and_print("")
        log_and_print("✓ Security updates monitoring completed")
        log_and_print(f"  Processed: {len(languages_to_process)} language(s)")
        log_and_print(f"  Successful: {successful_count} language(s)")

    except Exception as e:
        log_and_print(f"✗ Error monitoring security updates: {e}")
        logging.exception("Full traceback:")

    log_and_print("")
    log_and_print("-" * 60)
    log_and_print("Monitoring cycle completed")
    log_and_print("-" * 60)
    log_and_print("")


def main() -> None:
    """Main function to orchestrate the CrazyOnes workflow."""
    global _shutdown_requested

    # Set up logging first
    setup_logging()

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log_and_print("=" * 60)
    log_and_print("CrazyOnes - Apple Updates Monitoring System")
    log_and_print("=" * 60)
    log_and_print("")

    # Parse command line arguments
    args = parse_arguments()

    # Determine daemon mode and interval
    daemon_mode = args.daemon or args.interval is not None
    interval = args.interval if args.interval else 43200  # Default 12 hours (2 times per day)

    if daemon_mode:
        log_and_print(f"Running in DAEMON mode with {interval} seconds interval")
        log_and_print("")

    # Validate Telegram bot token format
    if not validate_telegram_token(args.token):
        error_msg = (
            "✗ Error: Invalid Telegram bot token format.\n"
            "Expected format: <bot_id>:<auth_token>\n"
            "  - bot_id: 8-10 digits\n"
            "  - auth_token: 35+ alphanumeric characters (can include - and _)\n"
            "Example: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
        )
        log_and_print(error_msg)
        log_only("Token validation failed", "ERROR")
        sys.exit(1)

    # Check if token is different from saved token
    try:
        config = load_config()
        saved_token = config.get("telegram_bot_token", "")

        # Check if tokens are different and saved token is not the placeholder
        if (saved_token and
            saved_token != "YOUR_TELEGRAM_BOT_TOKEN_HERE" and
            saved_token != args.token):
            # In daemon mode, don't ask for confirmation, use provided token
            if daemon_mode:
                log_and_print("Token mismatch detected. Using provided token in daemon mode.")
                token_to_use = args.token
            else:
                # Ask user which token to use
                use_new_token = ask_token_confirmation(args.token, saved_token)

                if use_new_token:
                    log_and_print("\n✓ Using NEW token (provided as parameter)")
                    log_only("User chose to use new token", "INFO")
                    token_to_use = args.token
                else:
                    log_and_print("\n✓ Using SAVED token (from config.json)")
                    log_only("User chose to use saved token", "INFO")
                    token_to_use = saved_token
        else:
            # No conflict, use provided token
            token_to_use = args.token
    except FileNotFoundError:
        # No config file exists yet, use provided token
        config = {}
        token_to_use = args.token

    # Save token and URL to config.json
    try:
        # Config was already loaded above when checking token
        if "config" not in locals():
            try:
                config = load_config()
            except FileNotFoundError:
                config = {}

        # Update token in config with the chosen token
        config["telegram_bot_token"] = token_to_use
        log_and_print(f"Telegram bot token: {'*' * 20} (configured)")

        # Save version to config
        config["version"] = __version__

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

    # Main execution loop
    if daemon_mode:
        log_and_print("Starting daemon mode...")
        log_and_print("Press Ctrl+C to stop gracefully")
        log_and_print("")

        while not _shutdown_requested:
            try:
                run_monitoring_cycle(apple_updates_url)

                if not _shutdown_requested:
                    log_and_print(f"Waiting {interval} seconds until next cycle...")
                    log_and_print("")

                    # Sleep in small intervals to respond quickly to shutdown signals
                    for _ in range(interval):
                        if _shutdown_requested:
                            break
                        time.sleep(1)

            except Exception as e:
                log_and_print(f"✗ Error in monitoring cycle: {e}")
                logging.exception("Full traceback:")
                if not _shutdown_requested:
                    log_and_print(f"Waiting {interval} seconds before retry...")
                    log_and_print("")
                    for _ in range(interval):
                        if _shutdown_requested:
                            break
                        time.sleep(1)

        log_and_print("")
        log_and_print("=" * 60)
        log_and_print("Daemon stopped gracefully")
        log_and_print("=" * 60)
        log_and_print("")

    else:
        # Single execution mode
        log_and_print("Running in SINGLE execution mode")
        log_and_print("")

        run_monitoring_cycle(apple_updates_url)

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
