"""Tests for the administrator-only /hash command."""

import asyncio
import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

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

    async def get_chat(self, chat_id: int) -> Any:
        return self.chats[chat_id]


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
