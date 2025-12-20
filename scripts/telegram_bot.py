#!/usr/bin/env python3
"""
Telegram bot module for Apple Updates notifications.

This bot communicates in English and allows users to subscribe to Apple Updates
in their preferred language. It tracks subscriptions and sends updates accordingly.
"""

import json
import logging
from pathlib import Path
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from .generate_language_names import LANGUAGE_NAME_MAP

# Subscriptions file path
SUBSCRIPTIONS_FILE = "data/subscriptions.json"

logger = logging.getLogger(__name__)

# Translations for different languages
TRANSLATIONS = {
    "en": {
        "welcome": (
            "🍎 *Welcome to Apple Updates Bot!*\n\n"
            "I'm a bot that notifies about Apple software updates.\n\n"
            "Please select the language of Apple Updates you want to "
            "monitor:"
        ),
        "no_languages": (
            "⚠️ Sorry, no languages are available at the moment. "
            "Please try again later."
        ),
        "language_selected": (
            "✅ *Language selected: {display_name}*\n\n"
            "You will now receive Apple Updates in this language."
        ),
        "no_updates": (
            "ℹ️ No updates available yet for this language. "
            "You'll be notified when new updates are published."
        ),
        "recent_updates_header": (
            "📱 *Here are the {count} most recent Apple Updates:*\n"
        ),
        "new_updates_header": "🔔 *New Apple Updates*\n",
    },
    "es": {
        "welcome": (
            "🍎 *¡Bienvenido al Bot de Actualizaciones de Apple!*\n\n"
            "Soy un bot que notifica sobre actualizaciones de software "
            "de Apple.\n\n"
            "Por favor selecciona el idioma de Apple Updates que quieres "
            "monitorizar:"
        ),
        "no_languages": (
            "⚠️ Lo siento, no hay idiomas disponibles en este momento. "
            "Por favor, inténtalo más tarde."
        ),
        "language_selected": (
            "✅ *Idioma seleccionado: {display_name}*\n\n"
            "Ahora recibirás las Actualizaciones de Apple en este idioma."
        ),
        "no_updates": (
            "ℹ️ Aún no hay actualizaciones disponibles para este idioma. "
            "Se te notificará cuando se publiquen nuevas actualizaciones."
        ),
        "recent_updates_header": (
            "📱 *Estas son las {count} actualizaciones más recientes de "
            "Apple:*\n"
        ),
        "new_updates_header": "🔔 *Nuevas actualizaciones de Apple*\n",
    },
}


def get_translation(lang_code: str, key: str, **kwargs: Any) -> str:
    """
    Get translated text for a given language code and key.

    Args:
        lang_code: Language code (e.g., 'en-us', 'es-es')
        key: Translation key
        **kwargs: Format arguments for the translation string

    Returns:
        Translated and formatted string
    """
    # Extract base language (e.g., 'en' from 'en-us')
    base_lang = lang_code.split("-")[0] if "-" in lang_code else lang_code

    # Default to English if translation not found
    translations = TRANSLATIONS.get(base_lang, TRANSLATIONS["en"])
    text = translations.get(key, TRANSLATIONS["en"].get(key, ""))

    return text.format(**kwargs) if kwargs else text


def load_subscriptions() -> dict[str, dict[str, Any]]:
    """
    Load subscriptions from JSON file.

    Returns:
        Dictionary with chat_id as keys and subscription data as values.
        Each subscription contains: language_code, last_update_index
    """
    path = Path(SUBSCRIPTIONS_FILE)
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as f:
        data: dict[str, dict[str, Any]] = json.load(f)
        return data


def save_subscriptions(subscriptions: dict[str, dict[str, Any]]) -> None:
    """
    Save subscriptions to JSON file.

    Args:
        subscriptions: Dictionary with chat_id as keys and subscription data
    """
    path = Path(SUBSCRIPTIONS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(subscriptions, f, indent=2, ensure_ascii=False)


def load_language_urls() -> dict[str, str]:
    """
    Load available language URLs.

    Returns:
        Dictionary mapping language codes to URLs
    """
    path = Path("data/language_urls.json")
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as f:
        data: dict[str, str] = json.load(f)
        return data


def load_updates_for_language(language_code: str) -> list[dict[str, Any]]:
    """
    Load updates for a specific language.

    Args:
        language_code: Language code (e.g., 'en-us')

    Returns:
        List of update dictionaries
    """
    path = Path(f"data/updates/{language_code}.json")
    if not path.exists():
        return []

    with open(path, encoding="utf-8") as f:
        data: list[dict[str, Any]] = json.load(f)
        return data


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command. Show welcome message and language selection.

    Args:
        update: Telegram update object
        context: Callback context
    """
    if not update.effective_chat or not update.message:
        return

    # Welcome message in English (bot interface is in English)
    welcome_message = get_translation("en", "welcome")

    # Load available languages
    language_urls = load_language_urls()

    if not language_urls:
        await update.message.reply_text(
            get_translation("en", "no_languages")
        )
        return

    # Create inline keyboard with language options
    # Format: "code: Language/Country"
    keyboard = []
    for lang_code in sorted(language_urls.keys()):
        display_name = LANGUAGE_NAME_MAP.get(
            lang_code, lang_code.upper().replace("-", "/")
        )
        button_text = f"{lang_code}: {display_name}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=lang_code)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def language_selection_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle language selection from inline keyboard.

    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    if not update.effective_chat:
        return

    chat_id = str(update.effective_chat.id)
    language_code = query.data

    # Load or create subscriptions
    subscriptions = load_subscriptions()

    # Check if this is a first-time subscription
    is_first_time = chat_id not in subscriptions

    # Save subscription with language and initial tracking
    last_idx = (
        -1 if is_first_time
        else subscriptions[chat_id].get("last_update_index", -1)
    )
    subscriptions[chat_id] = {
        "language_code": language_code,
        "last_update_index": last_idx,
    }
    save_subscriptions(subscriptions)

    # Get language display name
    display_name = LANGUAGE_NAME_MAP.get(
        language_code, language_code.upper().replace("-", "/")
    )

    # Send confirmation message in the selected language
    confirmation_message = get_translation(
        language_code, "language_selected", display_name=display_name
    )

    await query.edit_message_text(
        confirmation_message,
        parse_mode="Markdown"
    )

    # If first time, send the 10 most recent updates
    if is_first_time:
        await send_recent_updates(update, context, chat_id, language_code)


async def send_recent_updates(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: str,
    language_code: str,
) -> None:
    """
    Send the 10 most recent updates to a new subscriber.

    Args:
        update: Telegram update object
        context: Callback context
        chat_id: Chat ID to send updates to
        language_code: Language code for updates
    """
    # Load updates for the language
    updates = load_updates_for_language(language_code)

    if not updates:
        message = get_translation(language_code, "no_updates")
        await context.bot.send_message(
            chat_id=int(chat_id),
            text=message
        )
        return

    # Get the 10 most recent updates
    recent_updates = updates[:10]

    # Update the last_update_index to mark these as sent
    subscriptions = load_subscriptions()
    if chat_id in subscriptions:
        last_idx = 9 if len(updates) >= 10 else len(updates) - 1
        subscriptions[chat_id]["last_update_index"] = last_idx
        save_subscriptions(subscriptions)

    # Send header message
    header = get_translation(
        language_code, "recent_updates_header", count=len(recent_updates)
    )

    # Format updates based on language
    base_lang = language_code.split("-")[0] if "-" in language_code else language_code

    if base_lang == "es":
        # Spanish format: one update per line (date - name - target)
        message = header
        for update_item in recent_updates:
            date = update_item.get("date", "N/A")
            name = update_item.get("name", "Unknown")
            target = update_item.get("target", "N/A")
            url = update_item.get("url")

            if url:
                # Name as link
                update_line = f"{date} - [{name}]({url}) - {target}\n"
            else:
                update_line = f"{date} - {name} - {target}\n"

            message += update_line

        await context.bot.send_message(
            chat_id=int(chat_id),
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    else:
        # English format: detailed format with emojis (one message per update)
        await context.bot.send_message(
            chat_id=int(chat_id),
            text=header,
            parse_mode="Markdown"
        )

        for idx, update_item in enumerate(recent_updates, 1):
            message = format_update_message(update_item, idx, language_code)
            await context.bot.send_message(
                chat_id=int(chat_id),
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )


def format_update_message(
    update_item: dict[str, Any], number: int = 0, language_code: str = "en"
) -> str:
    """
    Format an update item into a Telegram message.

    Args:
        update_item: Update dictionary with name, target, date, and optional url
        number: Optional number prefix for the update
        language_code: Language code for formatting

    Returns:
        Formatted message string
    """
    name = update_item.get("name", "Unknown")
    target = update_item.get("target", "N/A")
    date = update_item.get("date", "N/A")
    url = update_item.get("url")

    # Get base language
    base_lang = language_code.split("-")[0] if "-" in language_code else language_code

    if base_lang == "es":
        # Spanish format: date - name - target (inline)
        if url:
            message = f"{date} - [{name}]({url}) - {target}"
        else:
            message = f"{date} - {name} - {target}"
    else:
        # English format: detailed with emojis
        if number > 0:
            message = f"*{number}. {name}*\n"
        else:
            message = f"*{name}*\n"

        message += f"📱 Target: {target}\n"
        message += f"📅 Date: {date}\n"

        if url:
            message += f"🔗 [More info]({url})"

    return message


def create_application(token: str) -> Application:  # type: ignore[type-arg]
    """
    Create and configure the Telegram bot application.

    Args:
        token: Telegram bot token

    Returns:
        Configured Application instance
    """
    # Create application
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))

    # Add callback query handler for language selection
    application.add_handler(CallbackQueryHandler(language_selection_callback))

    return application


async def send_new_updates_to_subscribers() -> None:
    """
    Check for new updates and send them to subscribers.
    This function should be called periodically by the main monitoring loop.
    """
    subscriptions = load_subscriptions()

    if not subscriptions:
        logger.info("No subscriptions found, skipping update notifications")
        return

    for chat_id, subscription_data in subscriptions.items():
        language_code = subscription_data.get("language_code")
        last_update_index = subscription_data.get("last_update_index", -1)

        if not language_code:
            continue

        # Load updates for this language
        updates = load_updates_for_language(language_code)

        if not updates:
            continue

        # Check if there are new updates (updates are ordered from newest to oldest)
        # If last_update_index is -1, user has already received initial updates
        # We need to find updates that are newer than what the user has seen
        if last_update_index == -1:
            # User has received initial updates, no new ones yet
            continue

        # Get new updates (indices 0 to last_update_index - 1)
        if last_update_index == 0:
            # User has seen the most recent update, check if there are
            # new ones at the beginning (after a new monitoring cycle)
            continue

        # TODO: This logic needs to be integrated with the bot's event loop
        # For now, we'll leave this as a placeholder for future integration
        logger.info(
            f"Would send updates to chat {chat_id} for "
            f"language {language_code}"
        )


async def start_bot(token: str) -> None:
    """
    Start the Telegram bot.

    Args:
        token: Telegram bot token
    """
    application = create_application(token)

    logger.info("Starting Telegram bot...")
    await application.initialize()
    await application.start()

    if application.updater:
        await application.updater.start_polling()
        logger.info("Bot is running. Press Ctrl+C to stop.")
        # Keep the bot running
        await application.updater.stop()

    await application.stop()
    await application.shutdown()
