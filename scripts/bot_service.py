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
from pathlib import Path
from typing import Any

from telegram.ext import Application

# Type alias for Application with all-Any type args (6 required by python-telegram-bot)
AnyApplication = Application[Any, Any, Any, Any, Any, Any]

try:
    # Try relative import (when used as a module)
    from .generate_language_names import LANGUAGE_NAME_MAP
    from .telegram_bot import (
        build_update_signature,
        create_application,
        get_translation,
        load_bot_version,
        load_config_version,
        load_subscriptions,
        load_updates_for_language,
        save_bot_version,
        save_subscriptions,
        send_version_notifications,
    )
except ImportError:
    # Fall back to absolute import (when run directly)
    from generate_language_names import (  # type: ignore[import-not-found,no-redef]
        LANGUAGE_NAME_MAP,
    )
    from telegram_bot import (  # type: ignore[import-not-found,no-redef]
        build_update_signature,
        create_application,
        get_translation,
        load_bot_version,
        load_config_version,
        load_subscriptions,
        load_updates_for_language,
        save_bot_version,
        save_subscriptions,
        send_version_notifications,
    )

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
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


async def check_for_new_updates(application: AnyApplication) -> None:
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
            trigger_data: dict[str, Any] = json.load(f)

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
    application: AnyApplication, updated_languages: list[str]
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
    subscriptions_changed = False

    for chat_id, subscription_data in subscriptions.items():
        if not subscription_data.get("active", False):
            continue

        language_code = subscription_data.get("language_code")
        if not language_code or language_code not in updated_languages:
            continue

        # Load updates for this language
        updates = load_updates_for_language(language_code)

        if not updates:
            continue

        last_update_signature = get_last_update_signature(subscription_data, updates)
        new_updates, latest_signature, marker_found = get_new_updates_since_signature(
            updates, last_update_signature
        )

        if latest_signature is None:
            continue

        if not new_updates:
            if not marker_found:
                logger.warning(
                    f"Previous update marker missing for chat {chat_id} "
                    f"(lang: {language_code}); resetting baseline"
                )
            subscriptions[chat_id]["last_update_signature"] = latest_signature
            latest_id = updates[0].get("id")
            if isinstance(latest_id, int):
                subscriptions[chat_id]["last_update_id"] = latest_id
            subscriptions_changed = True
            continue

        # Sort new updates by ID (oldest first)
        new_updates.sort(key=lambda x: x.get("id", 0))

        # Send notification
        try:
            await send_update_notification(
                application, chat_id, language_code, new_updates
            )

            subscriptions[chat_id]["last_update_signature"] = latest_signature
            latest_id = updates[0].get("id")
            if isinstance(latest_id, int):
                subscriptions[chat_id]["last_update_id"] = latest_id
            notification_count += 1
            subscriptions_changed = True

        except Exception as e:
            logger.error(f"Error sending notification to {chat_id}: {e}")

    # Save updated subscriptions
    if subscriptions_changed:
        save_subscriptions(subscriptions)
    if notification_count > 0:
        logger.info(f"Sent notifications to {notification_count} subscribers")
    elif subscriptions_changed:
        logger.info("Updated subscription markers without sending notifications")


def get_last_update_signature(
    subscription_data: dict[str, Any], updates: list[dict[str, Any]]
) -> str | None:
    """
    Resolve the last delivered update signature for a subscription.

    Args:
        subscription_data: Per-user subscription dictionary.
        updates: Current update list for the selected language.

    Returns:
        Last known update signature, if available.
    """
    signature = subscription_data.get("last_update_signature")
    if isinstance(signature, str) and signature:
        return signature

    legacy_id = subscription_data.get("last_update_id")
    if isinstance(legacy_id, int):
        for update_item in updates:
            if update_item.get("id") == legacy_id:
                return build_update_signature(update_item)

    return None


def get_new_updates_since_signature(
    updates: list[dict[str, Any]], last_signature: str | None
) -> tuple[list[dict[str, Any]], str | None, bool]:
    """
    Compute unseen updates using a content-based marker.

    Args:
        updates: Current language updates ordered from newest to oldest.
        last_signature: Previously delivered update signature.

    Returns:
        Tuple with:
        - unseen updates to notify (oldest first),
        - latest update signature for persistence,
        - whether the previous marker was found (or not needed).
    """
    if not updates:
        return [], None, True

    latest_signature = build_update_signature(updates[0])
    if not last_signature:
        return [], latest_signature, True

    new_updates: list[dict[str, Any]] = []
    for update_item in updates:
        if build_update_signature(update_item) == last_signature:
            new_updates.reverse()
            return new_updates, latest_signature, True
        new_updates.append(update_item)

    return [], latest_signature, False


async def send_update_notification(
    application: AnyApplication,
    chat_id: str,
    language_code: str,
    new_updates: list[dict[str, Any]],
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
    header = get_translation(language_code, "new_updates_header")
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
        disable_web_page_preview=True,
    )

    logger.info(f"Sent {len(new_updates)} updates to chat {chat_id}")


async def check_and_notify_new_version(application: AnyApplication) -> None:
    """
    Detect a new bot version and send release announcements to all active subscribers.

    Compares the version in config.json against the last version recorded in
    data/bot_version.json. When they differ, each active subscriber receives a
    short notification in their registered language summarising what changed.
    After notifications are dispatched the tracker file is updated so the
    announcements are sent only once per release.

    Args:
        application: The Telegram application instance
    """
    current_version = load_config_version()
    if not current_version:
        logger.warning(
            "Could not read version from config.json; skipping version check"
        )
        return

    version_data = load_bot_version()
    last_notified = version_data.get("last_notified_version", "")

    if current_version == last_notified:
        logger.info(f"Version {current_version} already announced; skipping")
        return

    logger.info(
        f"New version detected: {current_version} (was: {last_notified or 'none'})"
    )

    if last_notified:
        # Only notify when upgrading from a previously announced version, not on
        # the very first boot when there is no history yet.
        await send_version_notifications(application, current_version)

    # Record the current version so notifications fire only once
    version_data["last_notified_version"] = current_version
    save_bot_version(version_data)


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
    assert application.updater is not None, "Application must be built with an Updater"
    await application.updater.start_polling(
        allowed_updates=["message", "callback_query", "my_chat_member"]
    )
    logger.info("Bot is running and polling for updates")

    # Automatic version notifications are disabled; use /version verbose instead

    # Main loop: check for new updates periodically
    check_interval = 30  # Check every 30 seconds

    while not _shutdown_event.is_set():
        try:
            # Check for new updates
            await check_for_new_updates(application)

            # Wait for next check or shutdown
            try:
                await asyncio.wait_for(_shutdown_event.wait(), timeout=check_interval)
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
