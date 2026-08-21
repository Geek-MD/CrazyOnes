"""Tests for the administrator-only /hash command."""

import asyncio
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from scripts import telegram_bot


class DummyMessage:
    def __init__(self) -> None:
        self.replies: list[dict[str, Any]] = []

    async def reply_text(self, text: str, **kwargs: Any) -> None:
        self.replies.append({"text": text, **kwargs})


class DummyBot:
    def __init__(self, chats: dict[int, Any] | None = None) -> None:
        self.chats = chats or {}
        self.sent_messages: list[dict[str, Any]] = []

    async def get_chat(self, chat_id: int) -> Any:
        return self.chats[chat_id]

    async def send_message(self, **kwargs: Any) -> None:
        self.sent_messages.append(kwargs)


def write_updates(tmp_path: Path, updates: list[dict[str, Any]]) -> None:
    updates_dir = tmp_path / "data" / "updates"
    updates_dir.mkdir(parents=True, exist_ok=True)
    (updates_dir / "en-us.json").write_text(json.dumps(updates), encoding="utf-8")


def make_update() -> Any:
    return SimpleNamespace(
        effective_chat=SimpleNamespace(id=999, type="private"),
        effective_user=SimpleNamespace(id=42),
        message=DummyMessage(),
    )


def test_build_update_hash_uses_stable_signature() -> None:
    update_item = {
        "name": "iOS 30.1",
        "target": "iPhone",
        "date": "2026-08-12",
        "url": "https://example.com/update",
    }
    expected = hashlib.sha256(
        telegram_bot.build_update_signature(update_item).encode("utf-8")
    ).hexdigest()

    assert telegram_bot.build_update_hash(update_item) == expected


def test_record_notified_block_persists_latest_delivery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        telegram_bot, "UPDATE_BLOCKS_FILE", str(tmp_path / "update_blocks.json")
    )
    newest = {"name": "iOS 30.2", "target": "iPhone", "date": "2026-08-12"}
    oldest = {"name": "iOS 30.1", "target": "iPhone", "date": "2026-08-11"}
    monkeypatch.setattr(
        telegram_bot,
        "load_updates_for_language",
        lambda _language: [newest, oldest],
    )
    subscription: dict[str, Any] = {}

    telegram_bot.record_notified_block(subscription, "en-us", [oldest, newest])

    assert subscription["last_notified_update_signature"] == (
        telegram_bot.build_update_signature(newest)
    )
    assert subscription["last_notified_update_hash"] == telegram_bot.build_update_hash(
        newest
    )
    assert subscription["last_notified_at"].endswith("+00:00")


def test_last_update_hash_recovers_from_notified_block_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        telegram_bot, "UPDATE_BLOCKS_FILE", str(tmp_path / "update_blocks.json")
    )
    newest = {"name": "iOS 30.2", "target": "iPhone", "date": "2026-08-12"}
    oldest = {"name": "iOS 30.1", "target": "iPhone", "date": "2026-08-11"}
    monkeypatch.setattr(
        telegram_bot,
        "load_updates_for_language",
        lambda _language: [newest, oldest],
    )
    block_hash = telegram_bot.register_update_block("en-us", [oldest, newest])
    subscription = {
        "language_code": "en-us",
        "notified_update_blocks": [
            {"language_code": "en-us", "hash": block_hash, "count": 2}
        ],
    }

    assert telegram_bot.get_subscription_last_update_hash(subscription) == (
        telegram_bot.build_update_hash(newest)
    )


def test_last_update_hash_ignores_history_without_string_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        telegram_bot, "UPDATE_BLOCKS_FILE", str(tmp_path / "update_blocks.json")
    )
    subscription = {
        "language_code": "en-us",
        "notified_update_blocks": [{"language_code": "en-us", "hash": None}],
    }

    assert telegram_bot.get_subscription_last_update_hash(subscription) is None


def test_hash_command_lists_latest_updates(monkeypatch: pytest.MonkeyPatch) -> None:
    updates = [
        {"name": f"iOS 30.{index}", "target": "iPhone", "date": "2026-08-12"}
        for index in range(12)
    ]
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    monkeypatch.setattr(
        telegram_bot, "load_updates_for_language", lambda _language: updates
    )
    update = make_update()
    context = SimpleNamespace(args=[], bot=DummyBot())

    asyncio.run(telegram_bot.hash_command(update, context))

    report = "\n".join(reply["text"] for reply in update.message.replies)
    assert "iOS 30.0" in report
    assert "iOS 30.9" in report
    assert "iOS 30.10" not in report
    assert telegram_bot.build_update_hash(updates[0]) in report


def test_hash_command_lists_and_finds_subscribers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    signature = "iOS 30.1|iPhone|2026-08-12|"
    telegram_bot.save_subscriptions(
        {
            "123": {
                "active": True,
                "language_code": "en-us",
                "last_update_signature": signature,
            },
            "456": {"active": False, "language_code": "en-us"},
        }
    )
    chats = {123: SimpleNamespace(username="alice", title=None, full_name="Alice")}
    expected_hash = hashlib.sha256(signature.encode("utf-8")).hexdigest()

    list_update = make_update()
    list_context = SimpleNamespace(args=["subscribers"], bot=DummyBot(chats))
    asyncio.run(telegram_bot.hash_command(list_update, list_context))
    assert f"@alice — {expected_hash}" in list_update.message.replies[0]["text"]
    assert telegram_bot.load_subscriptions()["123"]["last_notified_update_hash"] == (
        expected_hash
    )

    user_update = make_update()
    user_context = SimpleNamespace(args=["alice"], bot=DummyBot(chats))
    asyncio.run(telegram_bot.hash_command(user_update, user_context))
    assert f"@alice — {expected_hash}" in user_update.message.replies[0]["text"]


def test_force_command_updates_named_active_subscriber(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    update_item = {
        "name": "iOS 30.2",
        "target": "iPhone",
        "date": "2026-08-12",
    }
    write_updates(tmp_path, [update_item])
    update_hash = telegram_bot.build_update_hash(update_item)
    telegram_bot.save_subscriptions(
        {
            "123": {
                "active": True,
                "language_code": "en-us",
                "chat_username": "alice",
                "last_update_block_hash": "obsolete",
            },
            "456": {"active": False, "chat_username": "inactive"},
        }
    )

    update = make_update()
    context = SimpleNamespace(args=["alice", update_hash], bot=DummyBot())
    asyncio.run(telegram_bot.force_command(update, context))

    subscriptions = telegram_bot.load_subscriptions()
    assert subscriptions["123"]["last_notified_update_hash"] == update_hash
    assert subscriptions["123"]["last_update_signature"] == (
        telegram_bot.build_update_signature(update_item)
    )
    assert "last_update_block_hash" not in subscriptions["123"]
    assert "last_notified_update_hash" not in subscriptions["456"]


def test_force_command_all_updates_only_active_subscribers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    update_item = {"name": "macOS 30.1", "target": "Mac", "date": "2026-08-12"}
    write_updates(tmp_path, [update_item])
    update_hash = telegram_bot.build_update_hash(update_item)
    telegram_bot.save_subscriptions(
        {
            "123": {"active": True, "chat_username": "alice"},
            "124": {"active": True, "chat_username": "team"},
            "456": {"active": False, "chat_username": "inactive"},
        }
    )

    update = make_update()
    context = SimpleNamespace(args=["all", update_hash], bot=DummyBot())
    asyncio.run(telegram_bot.force_command(update, context))

    subscriptions = telegram_bot.load_subscriptions()
    assert subscriptions["123"]["last_notified_update_hash"] == update_hash
    assert subscriptions["124"]["last_notified_update_hash"] == update_hash
    assert "last_notified_update_hash" not in subscriptions["456"]
    assert "2" in update.message.replies[0]["text"]


def test_force_command_rejects_unknown_hash_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    write_updates(tmp_path, [{"name": "iOS 30.2"}])
    telegram_bot.save_subscriptions({"123": {"active": True}})

    update = make_update()
    context = SimpleNamespace(args=["123", "0" * 64], bot=DummyBot())
    asyncio.run(telegram_bot.force_command(update, context))

    assert telegram_bot.load_subscriptions() == {"123": {"active": True}}


def test_force_updates_delivers_pending_and_preserves_automatic_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import bot_service

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    monkeypatch.setattr(
        telegram_bot, "UPDATE_BLOCKS_FILE", str(tmp_path / "update_blocks.json")
    )
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    previous = {
        "name": "iOS 30.1",
        "target": "iPhone",
        "date": "2026-08-11",
    }
    pending = {
        "name": "iOS 30.2",
        "target": "iPhone",
        "date": "2026-08-12",
    }
    write_updates(tmp_path, [pending, previous])
    telegram_bot.save_subscriptions(
        {
            "123": {
                "active": True,
                "language_code": "en-us",
                "last_update_signature": telegram_bot.build_update_signature(previous),
            }
        }
    )
    bot = DummyBot()
    application = SimpleNamespace(bot=bot)
    update = make_update()
    context = SimpleNamespace(args=["updates"], application=application, bot=bot)

    asyncio.run(telegram_bot.force_command(update, context))

    subscription = telegram_bot.load_subscriptions()["123"]
    assert len(bot.sent_messages) == 1
    assert "iOS 30.2" in bot.sent_messages[0]["text"]
    assert subscription["last_notified_update_hash"] == (
        telegram_bot.build_update_hash(pending)
    )
    assert subscription["last_update_signature"] == (
        telegram_bot.build_update_signature(pending)
    )
    assert subscription["last_update_block_hash"]

    future = {
        "name": "iOS 30.3",
        "target": "iPhone",
        "date": "2026-08-13",
    }
    write_updates(tmp_path, [future, pending, previous])

    assert asyncio.run(
        bot_service.send_new_updates_to_subscribers(application, ["en-us"])
    )

    subscription = telegram_bot.load_subscriptions()["123"]
    assert len(bot.sent_messages) == 2
    assert "iOS 30.3" in bot.sent_messages[1]["text"]
    assert "iOS 30.2" not in bot.sent_messages[1]["text"]
    assert subscription["last_notified_update_hash"] == (
        telegram_bot.build_update_hash(future)
    )


def test_force_updates_uses_confirmed_delivery_for_every_active_subscriber(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An advanced operational baseline must not hide an undelivered update."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    monkeypatch.setattr(
        telegram_bot, "UPDATE_BLOCKS_FILE", str(tmp_path / "update_blocks.json")
    )
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    previous = {
        "name": "iOS 30.1",
        "target": "iPhone",
        "date": "2026-08-11",
    }
    pending = {
        "name": "iOS 30.2",
        "target": "iPhone",
        "date": "2026-08-12",
    }
    updates = [pending, previous]
    write_updates(tmp_path, updates)
    current_block_hash = telegram_bot.register_update_block("en-us", updates)
    previous_signature = telegram_bot.build_update_signature(previous)
    pending_signature = telegram_bot.build_update_signature(pending)
    telegram_bot.save_subscriptions(
        {
            chat_id: {
                "active": True,
                "language_code": "en-us",
                # Simulate a baseline advanced without a confirmed Telegram send.
                "last_update_signature": pending_signature,
                "last_update_block_hash": current_block_hash,
                "last_notified_update_signature": previous_signature,
                "last_notified_update_hash": telegram_bot.build_update_hash(previous),
            }
            for chat_id in ("123", "456")
        }
    )
    bot = DummyBot()
    application = SimpleNamespace(bot=bot)
    update = make_update()
    context = SimpleNamespace(args=["updates"], application=application, bot=bot)

    asyncio.run(telegram_bot.force_command(update, context))

    assert {message["chat_id"] for message in bot.sent_messages} == {123, 456}
    subscriptions = telegram_bot.load_subscriptions()
    for chat_id in ("123", "456"):
        assert subscriptions[chat_id]["last_notified_update_hash"] == (
            telegram_bot.build_update_hash(pending)
        )
        assert subscriptions[chat_id]["last_notified_update_signature"] == (
            pending_signature
        )


def test_force_updates_recovers_orphaned_confirmed_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing confirmed marker must trigger a bounded recovery delivery."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        telegram_bot, "SUBSCRIPTIONS_FILE", str(tmp_path / "subscriptions.json")
    )
    monkeypatch.setattr(
        telegram_bot, "UPDATE_BLOCKS_FILE", str(tmp_path / "update_blocks.json")
    )
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: True)
    updates = [
        {
            "name": f"iOS 30.{index}",
            "target": "iPhone",
            "date": f"2026-08-{index:02d}",
        }
        for index in range(12, 0, -1)
    ]
    write_updates(tmp_path, updates)
    orphaned_signature = "Removed update|Old target|2026-07-01|"
    telegram_bot.save_subscriptions(
        {
            "123": {
                "active": True,
                "language_code": "en-us",
                "last_update_signature": telegram_bot.build_update_signature(
                    updates[0]
                ),
                "last_update_block_hash": telegram_bot.register_update_block(
                    "en-us", updates
                ),
                "last_notified_update_signature": orphaned_signature,
                "last_notified_update_hash": hashlib.sha256(
                    orphaned_signature.encode("utf-8")
                ).hexdigest(),
            }
        }
    )
    bot = DummyBot()
    application = SimpleNamespace(bot=bot)
    update = make_update()
    context = SimpleNamespace(args=["updates"], application=application, bot=bot)

    asyncio.run(telegram_bot.force_command(update, context))

    assert len(bot.sent_messages) == 1
    assert "iOS 30.12" in bot.sent_messages[0]["text"]
    assert "iOS 30.3" in bot.sent_messages[0]["text"]
    assert "iOS 30.2" not in bot.sent_messages[0]["text"]
    subscription = telegram_bot.load_subscriptions()["123"]
    assert subscription["last_notified_update_hash"] == (
        telegram_bot.build_update_hash(updates[0])
    )
    result_message = update.message.replies[-1]["text"]
    assert "Notified: 1" in result_message
    assert "Recovered markers: 1" in result_message


def test_force_updates_rejects_non_admin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(telegram_bot, "is_admin", lambda _user_id: False)
    unknown_command = AsyncMock()
    monkeypatch.setattr(telegram_bot, "handle_unknown_command", unknown_command)
    update = make_update()
    context = SimpleNamespace(args=["updates"], bot=DummyBot())

    asyncio.run(telegram_bot.force_command(update, context))

    unknown_command.assert_awaited_once_with(update, context)
    assert context.bot.sent_messages == []
