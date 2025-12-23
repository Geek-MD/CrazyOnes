#!/usr/bin/env python3
"""
Standalone Telegram bot for Apple Updates notifications.

This script runs the Telegram bot independently for debugging and testing.
It can be run separately from the main monitoring system.

Usage:
    python crazyones-bot.py                    # Use token from config.json
    python crazyones-bot.py -t YOUR_TOKEN      # Specify token directly
    python crazyones-bot.py --token YOUR_TOKEN # Long form
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from scripts.telegram_bot import create_application

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


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
            f"Please create a config.json file with your telegram_bot_token"
        )

    with open(config_path, encoding="utf-8") as f:
        config: dict[str, str] = json.load(f)

    return config


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="CrazyOnes Telegram Bot - Standalone mode for debugging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use token from config.json
  %(prog)s -t YOUR_TOKEN             # Specify token directly
  %(prog)s --token YOUR_TOKEN        # Long form
        """,
    )

    parser.add_argument(
        "-t",
        "--token",
        type=str,
        required=False,
        help="Telegram bot token (if not provided, reads from config.json)",
        metavar="TOKEN",
    )

    return parser.parse_args()


async def main() -> None:
    """Main function to run the Telegram bot."""
    # Parse command line arguments
    args = parse_arguments()

    # Get token from arguments or config file
    if args.token:
        token = args.token
        logger.info("Using token from command line argument")
    else:
        try:
            config = load_config()
            token = config.get("telegram_bot_token", "")
            if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
                logger.error("No valid token found in config.json")
                logger.error(
                    "Please provide a token with --token or update config.json"
                )
                sys.exit(1)
            logger.info("Using token from config.json")
        except FileNotFoundError as e:
            logger.error(str(e))
            logger.error("Please provide a token with --token argument")
            sys.exit(1)

    logger.info("=" * 60)
    logger.info("CrazyOnes Telegram Bot - Standalone Mode")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Starting Telegram bot...")
    logger.info(f"Token: {'*' * 20}...{token[-10:]}")
    logger.info("")

    # Create the application
    application = create_application(token)

    # Initialize the application
    await application.initialize()
    await application.start()

    # Start polling
    logger.info("Starting polling...")
    await application.updater.start_polling(
        allowed_updates=['message', 'callback_query', 'my_chat_member']
    )
    logger.info("✓ Bot is running and polling for updates")
    logger.info("")
    logger.info("Bot commands:")
    logger.info("  /start - Subscribe to Apple Updates notifications")
    logger.info("  /stop  - Unsubscribe from notifications")
    logger.info("  /about - Show information about the bot")
    logger.info("  /help  - Show help and available commands")
    logger.info("")
    logger.info("Press Ctrl+C to stop the bot")
    logger.info("=" * 60)

    # Keep the bot running
    try:
        # Run forever
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("")
        logger.info("Shutdown signal received. Stopping bot...")

    # Stop the bot gracefully
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

    logger.info("✓ Bot stopped successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Bot stopped by user")
        sys.exit(0)
