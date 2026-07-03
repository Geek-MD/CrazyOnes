#!/usr/bin/env python3
"""
Tests for update-notification marker logic in bot_service.py.
"""

from scripts.bot_service import (
    build_update_signature,
    get_last_update_signature,
    get_new_updates_since_signature,
)


def test_build_update_signature_includes_core_fields() -> None:
    """Signature should combine all fields used for update uniqueness."""
    update = {
        "id": 1,
        "name": "iOS 30.1",
        "target": "iPhone",
        "date": "2026-07-03",
        "url": "https://support.apple.com/12345",
    }

    signature = build_update_signature(update)
    assert signature == "iOS 30.1|iPhone|2026-07-03|https://support.apple.com/12345"


def test_get_new_updates_since_signature_returns_new_items_oldest_first() -> None:
    """Only updates before marker should be returned, ordered oldest->newest."""
    updates = [
        {"id": 1, "name": "iOS 30.2", "target": "iPhone", "date": "2026-07-03"},
        {"id": 2, "name": "iOS 30.1", "target": "iPhone", "date": "2026-07-01"},
        {"id": 3, "name": "iOS 30.0", "target": "iPhone", "date": "2026-06-29"},
    ]
    marker = build_update_signature(updates[1])

    new_updates, latest_signature, marker_found = get_new_updates_since_signature(
        updates, marker
    )

    assert marker_found is True
    assert latest_signature == build_update_signature(updates[0])
    assert [u["name"] for u in new_updates] == ["iOS 30.2"]


def test_get_new_updates_since_signature_without_marker_sets_baseline() -> None:
    """Missing marker should initialize baseline without sending backlog updates."""
    updates = [
        {"id": 1, "name": "iOS 30.2", "target": "iPhone", "date": "2026-07-03"},
        {"id": 2, "name": "iOS 30.1", "target": "iPhone", "date": "2026-07-01"},
    ]

    new_updates, latest_signature, marker_found = get_new_updates_since_signature(
        updates, None
    )

    assert marker_found is True
    assert new_updates == []
    assert latest_signature == build_update_signature(updates[0])


def test_get_new_updates_since_signature_missing_marker_resets_baseline() -> None:
    """Unknown marker should not notify all history and should reset marker safely."""
    updates = [
        {"id": 1, "name": "iOS 30.2", "target": "iPhone", "date": "2026-07-03"},
        {"id": 2, "name": "iOS 30.1", "target": "iPhone", "date": "2026-07-01"},
    ]

    new_updates, latest_signature, marker_found = get_new_updates_since_signature(
        updates, "nonexistent|marker"
    )

    assert marker_found is False
    assert new_updates == []
    assert latest_signature == build_update_signature(updates[0])


def test_get_last_update_signature_supports_legacy_id() -> None:
    """Legacy last_update_id should be converted to the new signature marker."""
    updates = [
        {"id": 1, "name": "iOS 30.2", "target": "iPhone", "date": "2026-07-03"},
        {"id": 2, "name": "iOS 30.1", "target": "iPhone", "date": "2026-07-01"},
    ]
    subscription = {"active": True, "language_code": "en-us", "last_update_id": 2}

    signature = get_last_update_signature(subscription, updates)

    assert signature == build_update_signature(updates[1])
