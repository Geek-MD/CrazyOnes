#!/usr/bin/env python3
"""
Telegram bot service that runs independently as a systemd service.

This service runs the Telegram bot in standalone mode, separate from the
monitoring/scraping service. It receives notifications about new updates
through a trigger file mechanism and sends them to subscribers.
"""

import asyncio
import json
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Any

from telegram.ext import Application

try:
    # Try relative import (when used as a module)
    from .telegram_bot import (
        create_application,
        load_subscriptions,
        load_updates_for_language,
        save_subscriptions,
        get_translation,
    )
    from .generate_language_names import LANGUAGE_NAME_MAP
except ImportError:
    # Fall back to absolute import (when run directly)
    from telegram_bot import (  # type: ignore[import-not-found]
        create_application,
        load_subscriptions,
        load_updates_for_language,
        save_subscriptions,
        get_translation,
    )
    from generate_language_names import LANGUAGE_NAME_MAP  # type: ignore[import-not-found]

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Trigger file for new updates
TRIGGER_FILE = "data/new_updates_trigger.json"

# Shutdown event
_shutdown_event = asyncio.Event()


def signal_handler(signum: int, frame: object) -> None:
    """Handle shutdown signals gracefully."""
    logger.info("Shutdown signal received")
    _shutdown_event.set()


async def check_for_new_updates(application: Application) -> None:
    """
    Check for new updates trigger file and notify subscribers.
    
    This function checks for a trigger file that is created by the monitoring
    service when new updates are detected. It then sends notifications to
    subscribers for updates they haven't received yet.
    
    Args:
        application: The Telegram application instance
    """
    trigger_path = Path(TRIGGER_FILE)
    
    if not trigger_path.exists():
        return
    
    logger.info("New updates trigger detected, processing notifications...")
    
    try:
        # Read and delete trigger file
        with open(trigger_path, encoding="utf-8") as f:
            trigger_data: dict[str, list[str]] = json.load(f)
        
        trigger_path.unlink()
        
        # Get updated languages
        updated_languages = trigger_data.get("updated_languages", [])
        
        if not updated_languages:
            logger.warning("Trigger file had no updated languages")
            return
        
        logger.info(f"Processing updates for {len(updated_languages)} languages")
        
        # Send notifications to subscribers
        await send_new_updates_to_subscribers(application, updated_languages)
        
    except Exception as e:
        logger.error(f"Error processing trigger file: {e}")
        # Delete trigger file even on error to avoid reprocessing
        try:
            trigger_path.unlink()
        except FileNotFoundError:
            pass


async def send_new_updates_to_subscribers(
    application: Application,
    updated_languages: list[str]
) -> None:
    """
    Send new updates to subscribers for the specified languages.
    
    Args:
        application: The Telegram application instance
        updated_languages: List of language codes that have new updates
    """
    subscriptions = load_subscriptions()
    
    if not subscriptions:
        logger.info("No subscriptions found")
        return
    
    notification_count = 0
    
    for chat_id, subscription_data in subscriptions.items():
        if not subscription_data.get("active", False):
            continue
        
        language_code = subscription_data.get("language_code")
        if not language_code or language_code not in updated_languages:
            continue
        
        # Get last_update_id (uses update ID instead of index)
        last_update_id = subscription_data.get("last_update_id", None)
        
        # Load updates for this language
        updates = load_updates_for_language(language_code)
        
        if not updates:
            continue
        
        # Find new updates (those with IDs not seen before)
        new_updates = []
        highest_id = last_update_id
        
        for update in updates:
            update_id = update.get("id")
            if update_id is None:
                continue
            
            # Track highest ID seen
            if highest_id is None or update_id > highest_id:
                highest_id = update_id
            
            # Add to new updates if we haven't sent it before
            if last_update_id is None or update_id > last_update_id:
                new_updates.append(update)
        
        if not new_updates:
            logger.debug(f"No new updates for chat {chat_id} (lang: {language_code})")
            continue
        
        # Sort new updates by ID (oldest first)
        new_updates.sort(key=lambda x: x.get("id", 0))
        
        # Send notification
        try:
            await send_update_notification(
                application, chat_id, language_code, new_updates
            )
            
            # Update last_update_id
            subscriptions[chat_id]["last_update_id"] = highest_id
            notification_count += 1
            
        except Exception as e:
            logger.error(f"Error sending notification to {chat_id}: {e}")
    
    # Save updated subscriptions
    if notification_count > 0:
        save_subscriptions(subscriptions)
        logger.info(f"Sent notifications to {notification_count} subscribers")


async def send_update_notification(
    application: Application,
    chat_id: str,
    language_code: str,
    new_updates: list[dict[str, Any]]
) -> None:
    """
    Send a notification about new updates to a subscriber.
    
    Args:
        application: The Telegram application instance
        chat_id: Chat ID to send notification to
        language_code: Language code for translations
        new_updates: List of new update dictionaries
    """
    # Get display name for the language
    display_name = LANGUAGE_NAME_MAP.get(
        language_code, language_code.upper().replace("-", "/")
    )
    
    # Build header message
    header = get_translation(
        language_code, "new_updates_header"
    )
    header += f"\n_{display_name}_\n\n"
    
    # Build message with updates
    message = header
    for idx, update in enumerate(new_updates, 1):
        date = update.get("date", "N/A")
        name = update.get("name", "Unknown")
        target = update.get("target", "N/A")
        url = update.get("url")
        
        # Format: Name[url] - Target - Date
        if url:
            update_line = f"{idx}. [{name}]({url}) - {target} - {date}\n"
        else:
            update_line = f"{idx}. {name} - {target} - {date}\n"
        
        message += update_line
    
    # Send message
    await application.bot.send_message(
        chat_id=int(chat_id),
        text=message,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    
    logger.info(f"Sent {len(new_updates)} updates to chat {chat_id}")


async def run_bot_service(token: str) -> None:
    """
    Run the bot service main loop.
    
    Args:
        token: Telegram bot token
    """
    logger.info("Starting bot service...")
    
    # Create application
    application = create_application(token)
    
    # Initialize and start
    await application.initialize()
    await application.start()
    
    # Start polling
    logger.info("Starting polling...")
    await application.updater.start_polling(
        allowed_updates=['message', 'callback_query', 'my_chat_member']
    )
    logger.info("Bot is running and polling for updates")
    
    # Main loop: check for new updates periodically
    check_interval = 30  # Check every 30 seconds
    
    while not _shutdown_event.is_set():
        try:
            # Check for new updates
            await check_for_new_updates(application)
            
            # Wait for next check or shutdown
            try:
                await asyncio.wait_for(
                    _shutdown_event.wait(),
                    timeout=check_interval
                )
                # If we get here, shutdown was triggered
                break
            except asyncio.TimeoutError:
                # Timeout is normal, continue to next iteration
                pass
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            # Wait a bit before retrying to avoid tight error loops
            await asyncio.sleep(5)
    
    # Cleanup
    logger.info("Stopping bot...")
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
    logger.info("Bot stopped successfully")


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


def main() -> None:
    """Main entry point for the bot service."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("CrazyOnes Bot Service")
    logger.info("=" * 60)
    
    # Load configuration
    try:
        config = load_config()
        token = config.get("telegram_bot_token", "")
        
        if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.error("No valid token found in config.json")
            sys.exit(1)
        
        logger.info("Token loaded from config.json")
        
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Run the service
    try:
        asyncio.run(run_bot_service(token))
    except KeyboardInterrupt:
        logger.info("Bot service interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in bot service: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Bot service shut down")


if __name__ == "__main__":
    main()
