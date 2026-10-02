"""Tests for SQLite persistence and the automatic legacy JSON migration."""

import json
import sqlite3
from pathlib import Path

import pytest

from scripts import database


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_first_run_migrates_runtime_json_and_removes_only_obsolete_files(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    db_path = data_dir / "crazyones.db"
    update = {
        "id": 1,
        "name": "iOS 30.1",
        "target": "iPhone",
        "date": "2026-09-01",
        "url": "https://example.test/update",
    }
    write_json(data_dir / "language_urls.json", {"en-us": "https://example.test"})
    write_json(data_dir / "language_names.json", {"en-us": "English/USA"})
    write_json(
        data_dir / "updates_tracking.json",
        {"en-us": {"url": "https://example.test", "hash": "table-hash"}},
    )
    write_json(data_dir / "updates" / "en-us.json", [update])
    write_json(
        data_dir / "subscriptions.json",
        {"123": {"active": True, "language_code": "en-us"}},
    )
    write_json(
        data_dir / "new_updates_trigger.json",
        {"updated_languages": ["en-us"]},
    )
    config = tmp_path / "config.json"
    translations = tmp_path / "scripts" / "translations" / "en-us.json"
    write_json(config, {"telegram_bot_token": "secret"})
    write_json(translations, {"hello": "Hello"})

    assert database.initialize_database(db_path) == db_path

    assert db_path.exists()
    assert not (data_dir / "language_urls.json").exists()
    assert not (data_dir / "subscriptions.json").exists()
    assert not (data_dir / "updates").exists()
    assert config.exists()
    assert translations.exists()
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT count(*) FROM languages").fetchone()[0] == 1
        assert (
            connection.execute("SELECT count(*) FROM localized_updates").fetchone()[0]
            == 1
        )
        assert (
            connection.execute("SELECT count(*) FROM subscriptions").fetchone()[0] == 1
        )
        assert connection.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1


def test_failed_migration_keeps_json_and_does_not_publish_database(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    source = data_dir / "subscriptions.json"
    source.parent.mkdir(parents=True)
    source.write_text("not-json", encoding="utf-8")
    db_path = data_dir / "crazyones.db"

    with pytest.raises(json.JSONDecodeError):
        database.initialize_database(db_path)

    assert source.exists()
    assert not db_path.exists()
    assert not db_path.with_suffix(".db.migrating").exists()


def test_sqlite_update_replacement_preserves_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "data" / "crazyones.db"
    monkeypatch.setattr(database, "DATABASE_FILE", db_path)
    database.initialize_database()
    database.save_languages({"en-us": "https://example.test"})
    old = {"id": 1, "name": "Old", "target": "Mac", "date": "2026-01-01"}
    new = {"id": 1, "name": "New", "target": "Mac", "date": "2026-02-01"}

    database.save_updates("en-us", [old])
    database.save_updates("en-us", [new])

    assert database.load_updates("en-us") == [new]
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, is_current FROM localized_updates ORDER BY name"
        ).fetchall()
    assert rows == [("New", 1), ("Old", 0)]
