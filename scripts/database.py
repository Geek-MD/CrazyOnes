# ruff: noqa: E501
"""SQLite persistence and one-time migration of CrazyOnes runtime JSON data."""

from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATABASE_FILE = Path(os.environ.get("CRAZYONES_DATABASE", "data/crazyones.db"))

_RUNTIME_JSON = (
    "language_urls.json",
    "language_names.json",
    "updates_tracking.json",
    "subscriptions.json",
    "update_blocks.json",
    "bot_version.json",
    "new_updates_trigger.json",
    "new_updates_trigger.processing.json",
    "scraping_errors_trigger.json",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;

        CREATE TABLE IF NOT EXISTS languages (
            code TEXT PRIMARY KEY,
            display_name TEXT,
            source_url TEXT NOT NULL,
            current_table_hash TEXT,
            last_checked_at TEXT,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS localized_updates (
            id INTEGER PRIMARY KEY,
            language_code TEXT NOT NULL REFERENCES languages(code) ON DELETE CASCADE,
            source_position INTEGER NOT NULL,
            name TEXT NOT NULL,
            target TEXT NOT NULL,
            release_date TEXT,
            info_url TEXT,
            signature TEXT NOT NULL,
            update_hash TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0, 1)),
            UNIQUE(language_code, signature)
        );
        CREATE INDEX IF NOT EXISTS idx_updates_recent
            ON localized_updates(language_code, is_current, source_position);
        CREATE INDEX IF NOT EXISTS idx_updates_hash ON localized_updates(update_hash);

        CREATE TABLE IF NOT EXISTS subscriptions (
            chat_id TEXT PRIMARY KEY,
            language_code TEXT,
            active INTEGER NOT NULL DEFAULT 0,
            chat_username TEXT,
            payload_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_subscriptions_active_language
            ON subscriptions(active, language_code);
        CREATE INDEX IF NOT EXISTS idx_subscriptions_username
            ON subscriptions(chat_username);

        CREATE TABLE IF NOT EXISTS update_blocks (
            id INTEGER PRIMARY KEY,
            language_code TEXT NOT NULL,
            block_hash TEXT NOT NULL,
            update_count INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(language_code, block_hash)
        );
        CREATE TABLE IF NOT EXISTS update_block_items (
            block_id INTEGER NOT NULL REFERENCES update_blocks(id) ON DELETE CASCADE,
            position INTEGER NOT NULL,
            update_signature TEXT NOT NULL,
            PRIMARY KEY(block_id, position)
        );
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            job_type TEXT NOT NULL,
            status TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_pending ON jobs(job_type, status, id);
        CREATE TABLE IF NOT EXISTS scraping_errors (
            id INTEGER PRIMARY KEY,
            occurred_at TEXT NOT NULL,
            source TEXT NOT NULL,
            message TEXT NOT NULL,
            context_json TEXT NOT NULL,
            notified_at TEXT
        );
        PRAGMA user_version = 1;
        """
    )


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _signature(item: dict[str, Any]) -> str:
    return "|".join(
        str(item.get(key, "")).strip() for key in ("name", "target", "date", "url")
    )


def _update_hash(signature: str) -> str:
    import hashlib

    return hashlib.sha256(signature.encode("utf-8")).hexdigest()


def _import_legacy(connection: sqlite3.Connection, data_dir: Path) -> None:
    now = utc_now()
    urls = _read_json(data_dir / "language_urls.json", {})
    names = _read_json(data_dir / "language_names.json", {})
    tracking = _read_json(data_dir / "updates_tracking.json", {})
    language_codes = set(urls) | set(names) | set(tracking)
    updates_dir = data_dir / "updates"
    if updates_dir.exists():
        language_codes.update(path.stem for path in updates_dir.glob("*.json"))
    for code in language_codes:
        state = tracking.get(code, {})
        connection.execute(
            "INSERT INTO languages(code, display_name, source_url, "
            "current_table_hash, updated_at) VALUES (?, ?, ?, ?, ?)",
            (
                code,
                names.get(code),
                urls.get(code, state.get("url", "")),
                state.get("hash"),
                now,
            ),
        )
    if updates_dir.exists():
        for path in sorted(updates_dir.glob("*.json")):
            for position, item in enumerate(_read_json(path, [])):
                signature = _signature(item)
                connection.execute(
                    "INSERT OR IGNORE INTO localized_updates(language_code, "
                    "source_position, name, target, release_date, info_url, signature, "
                    "update_hash, first_seen_at, last_seen_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        path.stem,
                        position,
                        str(item.get("name", "")),
                        str(item.get("target", "")),
                        item.get("date"),
                        item.get("url"),
                        signature,
                        _update_hash(signature),
                        now,
                        now,
                    ),
                )
    save_subscriptions(_read_json(data_dir / "subscriptions.json", {}), connection)
    blocks = _read_json(data_dir / "update_blocks.json", {})
    for language_code, language_blocks in blocks.items():
        for block_hash, block in language_blocks.items():
            save_update_block(
                language_code,
                block_hash,
                block.get("update_signatures", []),
                connection,
            )
    for key, value in _read_json(data_dir / "bot_version.json", {}).items():
        set_app_state(key, str(value), connection)
    for filename in ("new_updates_trigger.processing.json", "new_updates_trigger.json"):
        trigger = _read_json(data_dir / filename, {})
        if trigger.get("updated_languages"):
            enqueue_job("updates", trigger, connection)
    errors = _read_json(data_dir / "scraping_errors_trigger.json", {}).get("errors", [])
    for error in errors:
        add_scraping_error(
            str(error.get("source", "unknown")),
            str(error.get("message", "")),
            error.get("context", {}),
            str(error.get("timestamp", now)),
            connection,
        )


def initialize_database(path: Path | str | None = None) -> Path:
    """Create the database, importing and then deleting obsolete JSON on first run."""
    database = Path(path) if path is not None else DATABASE_FILE
    if database.exists():
        with _connect(database) as connection:
            _create_schema(connection)
        return database
    database.parent.mkdir(parents=True, exist_ok=True)
    temporary = database.with_suffix(database.suffix + ".migrating")
    temporary.unlink(missing_ok=True)
    try:
        with _connect(temporary) as connection:
            _create_schema(connection)
            with connection:
                _import_legacy(connection, database.parent)
            result = connection.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                raise RuntimeError(f"SQLite integrity check failed: {result}")
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            connection.execute("PRAGMA journal_mode = DELETE")
        os.replace(temporary, database)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    for filename in _RUNTIME_JSON:
        (database.parent / filename).unlink(missing_ok=True)
    updates_dir = database.parent / "updates"
    if updates_dir.exists():
        for update_file in updates_dir.glob("*.json"):
            update_file.unlink()
        try:
            updates_dir.rmdir()
        except OSError:
            pass
    return database


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    database = initialize_database()
    with _connect(database) as database_connection:
        yield database_connection


def load_languages() -> dict[str, str]:
    with connection() as db:
        return {
            row["code"]: row["source_url"]
            for row in db.execute(
                "SELECT code, source_url FROM languages ORDER BY code"
            )
        }


def save_languages(languages: dict[str, str]) -> None:
    now = utc_now()
    with connection() as db, db:
        existing = set(languages)
        for code, url in languages.items():
            db.execute(
                "INSERT INTO languages(code, source_url, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(code) DO UPDATE SET source_url=excluded.source_url, "
                "updated_at=excluded.updated_at",
                (code, url, now),
            )
        if existing:
            placeholders = ",".join("?" for _ in existing)
            db.execute(
                f"DELETE FROM languages WHERE code NOT IN ({placeholders})",
                tuple(existing),
            )


def load_tracking() -> dict[str, dict[str, str]]:
    with connection() as db:
        return {
            row["code"]: {"url": row["source_url"], "hash": row["current_table_hash"]}
            for row in db.execute(
                "SELECT code, source_url, current_table_hash FROM languages"
            )
            if row["current_table_hash"] is not None
        }


def save_tracking(tracking: dict[str, dict[str, str]]) -> None:
    now = utc_now()
    with connection() as db, db:
        for code, state in tracking.items():
            db.execute(
                "INSERT INTO languages(code, source_url, current_table_hash, updated_at) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(code) DO UPDATE SET "
                "source_url=excluded.source_url, current_table_hash=excluded.current_table_hash, "
                "last_checked_at=excluded.updated_at, updated_at=excluded.updated_at",
                (code, state.get("url", ""), state.get("hash"), now),
            )


def save_updates(language_code: str, updates: list[dict[str, Any]]) -> None:
    now = utc_now()
    with connection() as db, db:
        db.execute(
            "UPDATE localized_updates SET is_current=0 WHERE language_code=?",
            (language_code,),
        )
        for position, item in enumerate(updates):
            signature = _signature(item)
            db.execute(
                "INSERT INTO localized_updates(language_code, source_position, name, target, "
                "release_date, info_url, signature, update_hash, first_seen_at, last_seen_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(language_code, signature) "
                "DO UPDATE SET source_position=excluded.source_position, last_seen_at=excluded.last_seen_at, "
                "is_current=1",
                (
                    language_code,
                    position,
                    str(item.get("name", "")),
                    str(item.get("target", "")),
                    item.get("date"),
                    item.get("url"),
                    signature,
                    _update_hash(signature),
                    now,
                    now,
                ),
            )


def load_updates(language_code: str) -> list[dict[str, Any]]:
    with connection() as db:
        rows = db.execute(
            "SELECT source_position, name, target, release_date, info_url FROM "
            "localized_updates WHERE language_code=? AND is_current=1 "
            "ORDER BY source_position",
            (language_code,),
        ).fetchall()
    result = []
    for row in rows:
        item: dict[str, Any] = {
            "id": row["source_position"] + 1,
            "name": row["name"],
            "target": row["target"],
            "date": row["release_date"],
        }
        if row["info_url"]:
            item["url"] = row["info_url"]
        result.append(item)
    return result


def load_subscriptions() -> dict[str, dict[str, Any]]:
    with connection() as db:
        return {
            row["chat_id"]: json.loads(row["payload_json"])
            for row in db.execute(
                "SELECT chat_id, payload_json FROM subscriptions ORDER BY chat_id"
            )
        }


def save_subscriptions(
    data: dict[str, dict[str, Any]], db: sqlite3.Connection | None = None
) -> None:
    def write(target: sqlite3.Connection) -> None:
        target.execute("DELETE FROM subscriptions")
        now = utc_now()
        target.executemany(
            "INSERT INTO subscriptions(chat_id, language_code, active, chat_username, "
            "payload_json, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    str(chat_id),
                    item.get("language_code"),
                    int(bool(item.get("active", False))),
                    item.get("chat_username"),
                    json.dumps(item, ensure_ascii=False),
                    now,
                )
                for chat_id, item in data.items()
            ],
        )

    if db is not None:
        write(db)
    else:
        with connection() as target, target:
            write(target)


def save_subscription(chat_id: str, item: dict[str, Any]) -> None:
    """Insert or update one subscription without rewriting unrelated subscribers."""
    with connection() as db, db:
        db.execute(
            "INSERT INTO subscriptions(chat_id, language_code, active, chat_username, "
            "payload_json, updated_at) VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET language_code=excluded.language_code, "
            "active=excluded.active, chat_username=excluded.chat_username, "
            "payload_json=excluded.payload_json, updated_at=excluded.updated_at",
            (
                chat_id,
                item.get("language_code"),
                int(bool(item.get("active", False))),
                item.get("chat_username"),
                json.dumps(item, ensure_ascii=False),
                utc_now(),
            ),
        )


def load_update_blocks() -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    with connection() as db:
        rows = db.execute(
            "SELECT b.id, b.language_code, b.block_hash, b.update_count, "
            "i.update_signature FROM update_blocks b LEFT JOIN update_block_items i "
            "ON i.block_id=b.id ORDER BY b.id, i.position"
        )
        for row in rows:
            block = result.setdefault(row["language_code"], {}).setdefault(
                row["block_hash"],
                {"count": row["update_count"], "update_signatures": []},
            )
            if row["update_signature"] is not None:
                block["update_signatures"].append(row["update_signature"])
    return result


def save_update_block(
    language: str,
    block_hash: str,
    signatures: list[str],
    db: sqlite3.Connection | None = None,
) -> None:
    def write(target: sqlite3.Connection) -> None:
        target.execute(
            "INSERT OR IGNORE INTO update_blocks(language_code, block_hash, update_count, created_at) "
            "VALUES (?, ?, ?, ?)",
            (language, block_hash, len(signatures), utc_now()),
        )
        block_id = target.execute(
            "SELECT id FROM update_blocks WHERE language_code=? AND block_hash=?",
            (language, block_hash),
        ).fetchone()[0]
        target.executemany(
            "INSERT OR IGNORE INTO update_block_items(block_id, position, update_signature) "
            "VALUES (?, ?, ?)",
            [(block_id, i, value) for i, value in enumerate(signatures)],
        )

    if db is not None:
        write(db)
    else:
        with connection() as target, target:
            write(target)


def get_app_state() -> dict[str, str]:
    with connection() as db:
        return {
            row["key"]: row["value"]
            for row in db.execute("SELECT key, value FROM app_state")
        }


def set_app_state(key: str, value: str, db: sqlite3.Connection | None = None) -> None:
    target = db
    if target is not None:
        target.execute(
            "INSERT INTO app_state(key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) "
            "DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (key, value, utc_now()),
        )
    else:
        with connection() as opened, opened:
            set_app_state(key, value, opened)


def enqueue_job(
    job_type: str, payload: dict[str, Any], db: sqlite3.Connection | None = None
) -> None:
    if db is not None:
        db.execute(
            "INSERT INTO jobs(job_type, status, payload_json, created_at) VALUES (?, 'pending', ?, ?)",
            (job_type, json.dumps(payload, ensure_ascii=False), utc_now()),
        )
    else:
        with connection() as opened, opened:
            enqueue_job(job_type, payload, opened)


def claim_jobs(job_type: str) -> tuple[list[int], list[dict[str, Any]]]:
    with connection() as db, db:
        rows = db.execute(
            "SELECT id, payload_json FROM jobs WHERE job_type=? AND status='pending' ORDER BY id",
            (job_type,),
        ).fetchall()
        ids = [row["id"] for row in rows]
        if ids:
            db.executemany(
                "UPDATE jobs SET status='processing' WHERE id=?",
                [(item,) for item in ids],
            )
        return ids, [json.loads(row["payload_json"]) for row in rows]


def finish_jobs(ids: list[int], success: bool) -> None:
    if not ids:
        return
    with connection() as db, db:
        if success:
            db.executemany("DELETE FROM jobs WHERE id=?", [(item,) for item in ids])
        else:
            db.executemany(
                "UPDATE jobs SET status='pending' WHERE id=?", [(item,) for item in ids]
            )


def add_scraping_error(
    source: str,
    message: str,
    context: dict[str, Any],
    occurred_at: str | None = None,
    db: sqlite3.Connection | None = None,
) -> None:
    if db is not None:
        db.execute(
            "INSERT INTO scraping_errors(occurred_at, source, message, context_json) VALUES (?, ?, ?, ?)",
            (
                occurred_at or utc_now(),
                source,
                message,
                json.dumps(context, ensure_ascii=False),
            ),
        )
    else:
        with connection() as opened, opened:
            add_scraping_error(source, message, context, occurred_at, opened)


def claim_scraping_errors() -> list[dict[str, Any]]:
    with connection() as db, db:
        rows = db.execute(
            "SELECT id, occurred_at, source, message, context_json FROM scraping_errors "
            "WHERE notified_at IS NULL ORDER BY id"
        ).fetchall()
        now = utc_now()
        db.executemany(
            "UPDATE scraping_errors SET notified_at=? WHERE id=?",
            [(now, row["id"]) for row in rows],
        )
    return [
        {
            "timestamp": row["occurred_at"],
            "source": row["source"],
            "message": row["message"],
            "context": json.loads(row["context_json"]),
        }
        for row in rows
    ]
