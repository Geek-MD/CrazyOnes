"""Tests for first-time subscription baseline behavior."""

import asyncio
from pathlib import Path
from typing import Any

import pytest
from telegram import Chat

from scripts import telegram_bot


class DummyMessage:
    def __init__(self) -> None:
        self.replies: list[dict[str, Any]] = []

    async def reply_text(self, text: str, **kwargs: Any) -> None:
        self.replies.append({"text": text, **kwargs})


class DummyBot:
    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []

    async def send_message(self, **kwargs: Any) -> None:
        self.messages.append(kwargs)


class DummyUpdate:
    def __init__(self, chat_id: int = 123) -> None:
        self.effective_chat = type(
            "DummyChat", (), {"id": chat_id, "type": Chat.PRIVATE}
        )()
        self.message = DummyMessage()


class DummyContext:
    def __init__(self) -> None:
        self.bot = DummyBot()


def test_start_command_sends_latest_updates_and_records_baseline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A new /start subscription should receive and record the latest updates."""
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    updates = [
        {
            "id": index,
            "name": f"iOS 30.{index}",
            "target": "iPhone",
            "date": f"2026-07-{index:02d}",
            "url": f"https://example.com/{index}",
        }
        for index in range(12, 0, -1)
    ]
    monkeypatch.setattr(
        telegram_bot, "load_updates_for_language", lambda _lang: updates
    )

    update = DummyUpdate()
    context = DummyContext()

    asyncio.run(telegram_bot.start_command(update, context))  # type: ignore[arg-type]

    subscriptions = telegram_bot.load_subscriptions()
    subscription = subscriptions["123"]

    assert subscription["active"] is True
    assert subscription["language_code"] == telegram_bot.DEFAULT_LANGUAGE
    assert subscription["last_update_id"] == 12
    assert subscription["last_update_signature"] == telegram_bot.build_update_signature(
        updates[0]
    )
    assert len(update.message.replies) == 1
    assert len(context.bot.messages) == 11
    assert "10" in context.bot.messages[0]["text"]
    assert "iOS 30.12" in context.bot.messages[1]["text"]
    assert "iOS 30.3" in context.bot.messages[-1]["text"]


def test_start_command_existing_user_does_not_resend_latest_updates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An existing subscription should only be reactivated on /start."""
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    telegram_bot.save_subscriptions(
        {
            "123": {
                "language_code": "es-es",
                "active": False,
                "chat_type": Chat.PRIVATE,
                "last_update_id": 99,
                "last_update_signature": "existing|marker",
            }
        }
    )
    monkeypatch.setattr(telegram_bot, "load_updates_for_language", lambda _lang: [])

    update = DummyUpdate()
    context = DummyContext()

    asyncio.run(telegram_bot.start_command(update, context))  # type: ignore[arg-type]

    subscription = telegram_bot.load_subscriptions()["123"]

    assert subscription["active"] is True
    assert subscription["language_code"] == "es-es"
    assert subscription["last_update_id"] == 99
    assert subscription["last_update_signature"] == "existing|marker"
    assert len(context.bot.messages) == 0
