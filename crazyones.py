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

Note: Starting a new instance automatically stops any existing instance.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.generate_language_names import update_language_names

# Import monitor module at module level for efficiency
from scripts.monitor_apple_updates import (
    detect_changes,
    load_language_urls,
    load_tracking_data,
    process_language_url,
    save_tracking_data,
)

# Import the main functions from our scripts
from scripts.scrape_apple_updates import (
    extract_language_urls,
    fetch_apple_updates_page,
    save_language_urls_to_json,
)

# Version from pyproject.toml
__version__ = "0.15.0"

# PID file location
PID_FILE = "/tmp/crazyones.pid"

# Global event for graceful shutdown (thread-safe)
_shutdown_event = threading.Event()


def write_pid_file() -> None:
    """Write the current process ID to the PID file."""
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def read_pid_file() -> int | None:
    """Read PID from PID file. Returns None if file doesn't exist."""
    try:
        with open(PID_FILE) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def remove_pid_file() -> None:
    """Remove the PID file."""
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        # Sending signal 0 doesn't kill the process, just checks if it exists
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def stop_running_daemon() -> bool:
    """
    Stop a running daemon process.

    Returns:
        True if daemon was stopped, False if no daemon was running
    """
    pid = read_pid_file()
    if pid is None:
        print("No daemon PID file found.")
        return False

    if not is_process_running(pid):
        print(f"Daemon with PID {pid} is not running. Cleaning up PID file.")
        remove_pid_file()
        return False

    print(f"Stopping daemon process (PID: {pid})...")
    try:
        # Send SIGTERM for graceful shutdown
        os.kill(pid, signal.SIGTERM)
        print(f"SIGTERM sent to process {pid}. Daemon will stop gracefully.")
        remove_pid_file()
        return True
    except (OSError, ProcessLookupError) as e:
        print(f"Error stopping daemon: {e}")
        remove_pid_file()
        return False


def signal_handler(signum: int, frame: object) -> None:
    """
    Handle shutdown signals gracefully.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    _shutdown_event.set()
    log_and_print("\n\nShutdown signal received. Finishing current cycle...")
    # Clean up PID file on shutdown
    remove_pid_file()


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


def prompt_for_token() -> str:
    """
    Prompt user for Telegram bot token through TUI.

    Returns:
        Valid Telegram bot token

    Raises:
        KeyboardInterrupt: If user cancels the operation
    """
    print("\n" + "=" * 60)
    print("CrazyOnes Configuration")
    print("=" * 60)
    print("\nThis configuration wizard will help you set up CrazyOnes")
    print("to run as a systemd service on your device.")
    print()

    while True:
        try:
            print("Please enter your Telegram bot token.")
            print("You can get one from @BotFather on Telegram.")
            print()
            token = input("Telegram Bot Token: ").strip()

            if not token:
                print("\n✗ Error: Token cannot be empty.")
                print()
                continue

            if validate_telegram_token(token):
                print("\n✓ Token format is valid!")
                return token
            else:
                print("\n✗ Error: Invalid token format.")
                print("Expected format: <bot_id>:<auth_token>")
                print("  - bot_id: 8-10 digits")
                print("  - auth_token: 35+ alphanumeric characters")
                print("Example: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890")
                print()

        except (EOFError, KeyboardInterrupt):
            print("\n\nConfiguration cancelled by user.")
            raise


def prompt_for_url() -> str:
    """
    Prompt user for Apple Updates URL (optional).

    Returns:
        Apple Updates URL (default if not provided)
    """
    default_url = "https://support.apple.com/en-us/100100"

    print()
    print("Please enter the Apple Updates URL to monitor.")
    print(f"Press Enter to use the default: {default_url}")
    print()

    try:
        url = input("Apple Updates URL [default]: ").strip()

        if not url:
            print(f"\n✓ Using default URL: {default_url}")
            return default_url

        print(f"\n✓ Using URL: {url}")
        return url

    except (EOFError, KeyboardInterrupt):
        print("\n\nConfiguration cancelled by user.")
        raise


def generate_systemd_service_content(
    python_path: str,
    script_path: str,
    work_dir: str,
    user: str,
) -> str:
    """
    Generate systemd service file content.

    Args:
        python_path: Path to Python interpreter
        script_path: Path to crazyones.py script
        work_dir: Working directory for the service
        user: User to run the service as

    Returns:
        Systemd service file content
    """
    service_content = f"""[Unit]
Description=CrazyOnes - Apple Updates Monitoring Service
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={work_dir}
ExecStart={python_path} {script_path} --daemon --interval 21600
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=crazyones

[Install]
WantedBy=multi-user.target
"""
    return service_content


def install_systemd_service() -> bool:
    """
    Generate and install systemd service file.

    Returns:
        True if successful, False otherwise
    """
    try:
        import getpass
        import subprocess

        # Get current user
        current_user = getpass.getuser()

        # Get Python interpreter path
        python_path = sys.executable

        # Get script path
        script_path = Path(__file__).resolve()

        # Get working directory (where the script is located)
        work_dir = script_path.parent

        print()
        print("=" * 60)
        print("Systemd Service Installation")
        print("=" * 60)
        print()
        print(f"Python interpreter: {python_path}")
        print(f"Script location:    {script_path}")
        print(f"Working directory:  {work_dir}")
        print(f"Service user:       {current_user}")
        print()

        # Generate service content
        service_content = generate_systemd_service_content(
            python_path=python_path,
            script_path=str(script_path),
            work_dir=str(work_dir),
            user=current_user,
        )

        # Service file path
        service_name = "crazyones.service"
        service_path = Path(f"/etc/systemd/system/{service_name}")

        print("This will create a systemd service that:")
        print("  - Runs in daemon mode with 12-hour intervals")
        print("  - Starts automatically on system boot")
        print("  - Restarts automatically if it crashes")
        print()
        print("⚠ Note: This requires sudo/root privileges.")
        print()

        # Check if running as root
        if os.geteuid() != 0:
            print("Attempting to install service with sudo...")
            print("You may be prompted for your password.")
            print()

            # Write service content to temporary file with secure permissions
            import tempfile

            # Create a temporary file with secure permissions
            # (0o600 = owner read/write only)
            # Use system's secure temporary directory
            tmp_fd, tmp_service_path_str = tempfile.mkstemp(
                suffix=".service",
                prefix="crazyones_",
            )
            tmp_service_path = Path(tmp_service_path_str)

            try:
                # Explicitly set secure permissions on the file descriptor
                os.fchmod(tmp_fd, 0o600)

                # Write to the file descriptor with secure permissions
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                    f.write(service_content)

                # Copy service file with sudo
                result = subprocess.run(
                    ["sudo", "cp", str(tmp_service_path), str(service_path)],
                    capture_output=True,
                    text=True,
                    timeout=60,  # 60 second timeout for sudo password prompt
                )

                if result.returncode != 0:
                    print(f"✗ Error copying service file: {result.stderr}")
                    return False

                # Set proper permissions
                result = subprocess.run(
                    ["sudo", "chmod", "644", str(service_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    print(f"✗ Error setting permissions: {result.stderr}")
                    return False

            finally:
                # Clean up temporary file
                try:
                    tmp_service_path.unlink()
                except (FileNotFoundError, PermissionError, OSError):
                    # Silently ignore cleanup errors
                    pass

        else:
            # Running as root, write directly
            with open(service_path, "w", encoding="utf-8") as f:
                f.write(service_content)
            os.chmod(service_path, 0o644)

        print(f"✓ Service file created: {service_path}")

        # Reload systemd daemon
        print("Reloading systemd daemon...")
        is_root = os.geteuid() == 0
        cmd = (
            ["systemctl", "daemon-reload"]
            if is_root
            else ["sudo", "systemctl", "daemon-reload"]
        )
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired:
            print("✗ Error: systemctl daemon-reload timed out")
            print("   This may indicate system overload or systemd issues.")
            print("   Try running manually: sudo systemctl daemon-reload")
            return False

        if result.returncode != 0:
            print(f"✗ Error reloading systemd: {result.stderr}")
            return False

        print("✓ Systemd daemon reloaded")

        # Enable service
        print("Enabling service to start on boot...")
        cmd = (
            ["systemctl", "enable", service_name]
            if is_root
            else ["sudo", "systemctl", "enable", service_name]
        )
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired:
            print("✗ Error: systemctl enable timed out")
            print(f"   Try running manually: sudo systemctl enable {service_name}")
            return False

        if result.returncode != 0:
            print(f"✗ Error enabling service: {result.stderr}")
            return False

        print("✓ Service enabled")

        # Start service
        print("Starting service...")
        cmd = (
            ["systemctl", "start", service_name]
            if is_root
            else ["sudo", "systemctl", "start", service_name]
        )
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired:
            print("✗ Error: systemctl start timed out")
            print(f"   Try running manually: sudo systemctl start {service_name}")
            return False

        if result.returncode != 0:
            print(f"✗ Error starting service: {result.stderr}")
            return False

        print("✓ Service started")

        print()
        print("=" * 60)
        print("Service Installation Complete!")
        print("=" * 60)
        print()
        print("Useful commands:")
        print(f"  sudo systemctl status {service_name}   # Check service status")
        print(f"  sudo systemctl stop {service_name}     # Stop the service")
        print(f"  sudo systemctl restart {service_name}  # Restart the service")
        print(f"  sudo journalctl -u {service_name} -f   # View service logs")
        print()

        return True

    except subprocess.TimeoutExpired as e:
        print(f"\n✗ Error: Command timed out: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error installing systemd service: {e}")
        return False


def run_configuration_routine() -> bool:
    """
    Run the complete configuration routine.

    Returns:
        True if configuration completed successfully, False otherwise
    """
    try:
        # Step 1: Prompt for token
        token = prompt_for_token()

        # Step 2: Prompt for URL
        url = prompt_for_url()

        # Step 3: Save configuration
        print()
        print("Saving configuration...")

        config = {
            "version": __version__,
            "telegram_bot_token": token,
            "apple_updates_url": url,
        }

        save_config(config)
        print("✓ Configuration saved to config.json")

        # Step 4: Install systemd service
        success = install_systemd_service()

        if success:
            print()
            print("=" * 60)
            print("Configuration completed successfully!")
            print("=" * 60)
            print()
            return True
        else:
            print()
            print("=" * 60)
            print("Configuration completed with warnings")
            print("=" * 60)
            print()
            print("The token and URL have been saved to config.json,")
            print("but the systemd service could not be installed.")
            print("You can still run CrazyOnes manually with:")
            print("  python crazyones.py --daemon")
            print()
            return False

    except (KeyboardInterrupt, EOFError):
        print()
        print("Configuration cancelled.")
        return False


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
  %(prog)s                 # Run configuration wizard
  %(prog)s --config        # Run configuration wizard
  %(prog)s -t YOUR_TOKEN
  %(prog)s --token YOUR_TOKEN --url https://support.apple.com/en-us/100100
  %(prog)s -t YOUR_TOKEN -u https://support.apple.com/es-es/100100
  %(prog)s -t YOUR_TOKEN --daemon
  %(prog)s -t YOUR_TOKEN --interval 21600  # Check every 6 hours
  %(prog)s --log  # Show last 100 lines of log
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

    # Add log viewing argument (doesn't require token)
    parser.add_argument(
        "--log",
        action="store_true",
        help="Show last 100 lines of log file and exit",
    )

    # Add token argument (not required if using --log)
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        required=False,
        help="Telegram bot token (required for execution, not needed for --log)",
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
        help=(
            "Run as daemon (continuous monitoring with 6 hour interval, "
            "4 times per day)"
        ),
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        help=(
            "Monitoring interval in seconds (implies daemon mode, "
            "default: 21600 = 6 hours)"
        ),
        metavar="SECONDS",
    )

    parser.add_argument(
        "-b",
        "--bot",
        action="store_true",
        help="Start Telegram bot (requires daemon mode)",
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help=(
            "Run configuration routine to set up Telegram bot token "
            "and systemd service"
        ),
    )

    # Hidden parameter for testing - not shown in help
    parser.add_argument(
        "--once",
        action="store_true",
        help=argparse.SUPPRESS,  # Hide from help output
    )

    return parser.parse_args()


def show_log_tail(log_file: str = "crazyones.log", lines: int = 100) -> None:
    """
    Display the last N lines of the log file.

    Args:
        log_file: Path to the log file
        lines: Number of lines to show (default: 100)
    """
    log_path = Path(log_file)

    if not log_path.exists():
        print(f"Log file not found: {log_file}")
        print("The log file will be created when crazyones runs for the first time.")
        return

    try:
        with open(log_path, encoding='utf-8') as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            print("=" * 60)
            print(f"Last {len(tail_lines)} lines of {log_file}")
            print("=" * 60)
            print()

            for line in tail_lines:
                print(line, end='')

            print()
            print("=" * 60)
            print(f"Total lines in log: {len(all_lines)}")
            print("=" * 60)
    except Exception as e:
        print(f"Error reading log file: {e}")


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
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_and_print(f"Monitoring cycle started at {timestamp}")
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
        # Load language URLs
        try:
            language_urls = load_language_urls()
            log_and_print(f"Loaded {len(language_urls)} language URLs")
        except FileNotFoundError as e:
            log_and_print(f"✗ Error: {e}")
            log_and_print(
                "Language URLs file not found. "
                "Skipping security updates monitoring."
            )
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
    # Parse command line arguments
    args = parse_arguments()

    # Handle --log command (doesn't require token or setup)
    if args.log:
        show_log_tail()
        sys.exit(0)

    # Handle --config or no arguments (configuration routine)
    # Check if user wants config wizard: explicit --config flag,
    # or no execution flags provided
    should_run_config = not any(
        [args.token, args.daemon, args.interval, args.bot, args.once]
    )
    if args.config or should_run_config:
        success = run_configuration_routine()
        sys.exit(0 if success else 1)

    # Validate token is provided for normal execution (not needed for --once)
    if not args.token and not args.once:
        print("Error: --token is required for execution")
        print("Use --help for usage information, --log to view log file,")
        print("or run without arguments to start the configuration wizard")
        sys.exit(1)

    # Set up logging
    setup_logging()

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log_and_print("=" * 60)
    log_and_print("CrazyOnes - Apple Updates Monitoring System")
    log_and_print("=" * 60)
    log_and_print("")

    # Determine daemon mode and interval
    daemon_mode = args.daemon or args.interval is not None
    # Default 6 hours (4 times per day)
    interval = args.interval if args.interval else 21600
    bot_mode = args.bot
    once_mode = args.once  # Hidden parameter for testing

    # Validate bot mode
    if bot_mode and not daemon_mode:
        log_and_print("Error: --bot requires --daemon mode")
        log_and_print("Use --help for usage information")
        sys.exit(1)

    # Check if another instance is already running
    existing_pid = read_pid_file()
    if existing_pid and is_process_running(existing_pid):
        log_and_print(f"⚠ Detected existing CrazyOnes process (PID: {existing_pid})")
        log_and_print("Stopping existing process to start with new parameters...")
        stop_running_daemon()
        time.sleep(1)  # Give the old process a moment to clean up
        log_and_print("✓ Previous process stopped")
        log_and_print("")

    if daemon_mode:
        log_and_print(f"Running in DAEMON mode with {interval} seconds interval")
        # Write PID file for daemon mode
        write_pid_file()
        log_and_print(f"Daemon PID: {os.getpid()}")
        log_and_print("")

    # Validate Telegram bot token format (skip for --once mode)
    if not once_mode:
        if not validate_telegram_token(args.token):
            error_msg = (
                "✗ Error: Invalid Telegram bot token format.\n"
                "Expected format: <bot_id>:<auth_token>\n"
                "  - bot_id: 8-10 digits\n"
                "  - auth_token: 35+ alphanumeric characters "
                "(can include - and _)\n"
                "Example: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
            )
            log_and_print(error_msg)
            log_only("Token validation failed", "ERROR")
            sys.exit(1)

    # Check if token is different from saved token
    try:
        config = load_config()
        saved_token = config.get("telegram_bot_token", "")

        # For --once mode, we don't need a token
        if once_mode:
            token_to_use = saved_token  # Use saved token or empty string
        elif (saved_token and
            saved_token != "YOUR_TELEGRAM_BOT_TOKEN_HERE" and
            saved_token != args.token):
            # In daemon mode, don't ask, use provided token
            if daemon_mode:
                log_and_print(
                    "Token mismatch detected. "
                    "Using provided token in non-interactive mode."
                )
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
        # No config file exists yet
        if once_mode:
            token_to_use = ""  # No token needed for --once
        else:
            config = {}
            token_to_use = args.token

    # Save token and URL to config.json (skip token save for --once mode)
    try:
        # Config was already loaded above when checking token
        if "config" not in locals():
            try:
                config = load_config()
            except FileNotFoundError:
                config = {}

        # Update token in config with the chosen token (skip for --once mode)
        if not once_mode:
            config["telegram_bot_token"] = token_to_use
            log_and_print(f"Telegram bot token: {'*' * 20} (configured)")
        else:
            log_and_print("Running in ONCE mode (token not required)")

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

        # Save updated config (only if not in --once mode or if URL changed)
        if not once_mode or args.url:
            save_config(config)
            if once_mode:
                log_and_print("✓ Configuration saved to config.json")
            else:
                log_and_print("✓ Token and configuration saved to config.json")

    except Exception as e:
        log_and_print(f"⚠ Warning: Could not save to config.json: {e}")
        # Continue with provided values even if save fails
        apple_updates_url = args.url if args.url else ""
        if not apple_updates_url:
            log_and_print("Error: No URL available")
            sys.exit(1)

    log_and_print("")

    # Start Telegram bot if requested
    bot_application = None
    bot_thread = None
    if bot_mode:
        log_and_print("Starting Telegram bot...")
        from scripts.telegram_bot import create_application

        bot_application = create_application(token_to_use)

        # Run bot in a separate thread with its own event loop
        def run_bot_in_thread() -> None:
            """Run bot in a separate thread with its own async event loop."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def start_bot_async() -> None:
                try:
                    await bot_application.initialize()
                    await bot_application.start()
                    if bot_application.updater:
                        await bot_application.updater.start_polling()
                        log_and_print("✓ Telegram bot started successfully")
                        log_and_print("")

                        # Keep bot running until shutdown
                        while not _shutdown_event.is_set():
                            await asyncio.sleep(1)

                        # Cleanup
                        await bot_application.updater.stop()
                    await bot_application.stop()
                    await bot_application.shutdown()
                except Exception as e:
                    log_and_print(f"✗ Error in bot thread: {e}")
                    logging.exception("Full traceback:")

            try:
                loop.run_until_complete(start_bot_async())
            finally:
                loop.close()

        bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
        bot_thread.start()

        # Give bot a moment to start
        time.sleep(2)

    # Main execution loop
    if daemon_mode:
        log_and_print("Starting daemon mode...")
        log_and_print("Press Ctrl+C to stop gracefully")
        log_and_print("")

        while not _shutdown_event.is_set():
            try:
                run_monitoring_cycle(apple_updates_url)

                if not _shutdown_event.is_set():
                    log_and_print(f"Waiting {interval} seconds until next cycle...")
                    log_and_print("")

                    # Use event.wait() for efficient sleeping that can be interrupted
                    _shutdown_event.wait(timeout=interval)

            except Exception as e:
                log_and_print(f"✗ Error in monitoring cycle: {e}")
                logging.exception("Full traceback:")
                if not _shutdown_event.is_set():
                    log_and_print(f"Waiting {interval} seconds before retry...")
                    log_and_print("")
                    # Use event.wait() for efficient sleeping that can be interrupted
                    _shutdown_event.wait(timeout=interval)

        log_and_print("")
        log_and_print("=" * 60)
        log_and_print("Daemon stopped gracefully")
        log_and_print("=" * 60)
        log_and_print("")

        # Clean up PID file on normal exit
        remove_pid_file()

    else:
        # Single execution mode
        if once_mode:
            log_and_print("Running in ONCE mode (single execution for testing)")
        else:
            log_and_print("Running in SINGLE execution mode")
        log_and_print("")

        run_monitoring_cycle(apple_updates_url)

        log_and_print("")
        log_and_print("=" * 60)
        log_and_print("Workflow completed")
        log_and_print("=" * 60)
        log_and_print("")
        if once_mode:
            log_and_print("Execution summary:")
            log_and_print("  ✓ Language URLs scraped and saved")
            log_and_print("  ✓ Security updates processed for all languages")
            log_and_print("  ✓ All JSON files generated with proper sorting:")
            log_and_print("    - Language files: alphabetically sorted")
            log_and_print("    - Update files: sorted by ID (ascending, oldest first)")
            log_and_print("")
            log_and_print("Files generated:")
            log_and_print("  - data/language_urls.json")
            log_and_print("  - data/language_names.json")
            log_and_print("  - data/updates_tracking.json")
            log_and_print("  - data/updates/<lang-code>.json (one per language)")
            log_and_print("")
        else:
            log_and_print("Next steps:")
            log_and_print("  - Language URLs saved to: data/language_urls.json")
            log_and_print("  - Language names saved to: data/language_names.json")
            log_and_print(
                "  - You can now run: python -m scripts.monitor_apple_updates"
            )
            log_and_print("")


if __name__ == "__main__":
    main()
