"""Tiny SQLite persistence for mutable state (job cards, findings, audit log).

Read-only grid data stays in pandas; only things the UI creates/edits live here.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from app.config import get_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS job_cards (
    id            TEXT PRIMARY KEY,
    payload       TEXT NOT NULL,
    status        TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS findings (
    job_card_id   TEXT PRIMARY KEY,
    payload       TEXT NOT NULL,
    submitted_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
    id            TEXT PRIMARY KEY,
    actor         TEXT NOT NULL,
    timestamp     TEXT NOT NULL,
    action        TEXT NOT NULL,
    object_id     TEXT NOT NULL,
    result        TEXT NOT NULL
);
"""


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(get_settings().db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(_SCHEMA)


# -- job cards -----------------------------------------------------------
def list_job_cards() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT payload FROM job_cards ORDER BY created_at DESC").fetchall()
    return [json.loads(r["payload"]) for r in rows]


def get_job_card(card_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT payload FROM job_cards WHERE id = ?", (card_id,)).fetchone()
    return json.loads(row["payload"]) if row else None


def upsert_job_card(card: dict) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO job_cards (id, payload, status, created_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, status=excluded.status",
            (card["id"], json.dumps(card), card["status"], card["createdAt"]),
        )


def job_card_exists(card_id: str) -> bool:
    with connect() as conn:
        return conn.execute("SELECT 1 FROM job_cards WHERE id = ?", (card_id,)).fetchone() is not None


def count_job_cards() -> int:
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM job_cards").fetchone()["n"]


# -- findings ----------------------------------------------------------
def get_finding(job_card_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT payload FROM findings WHERE job_card_id = ?", (job_card_id,)
        ).fetchone()
    return json.loads(row["payload"]) if row else None


def upsert_finding(finding: dict) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO findings (job_card_id, payload, submitted_at) VALUES (?, ?, ?) "
            "ON CONFLICT(job_card_id) DO UPDATE SET payload=excluded.payload, "
            "submitted_at=excluded.submitted_at",
            (finding["jobCardId"], json.dumps(finding), finding["submittedAt"]),
        )


# -- audit -----------------------------------------------------------
def list_audit_events(limit: int = 100) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, actor, timestamp, action, object_id AS objectId, result "
            "FROM audit_events ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def list_audit_events_for_object(object_id: str, limit: int = 200) -> list[dict]:
    """All audit events recorded against one object (e.g. a consumer_id) —
    used by the agentic layer's dedup/recidivism safeguards so they see the
    live pipeline's own history instead of a separate log."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, actor, timestamp, action, object_id AS objectId, result "
            "FROM audit_events WHERE object_id = ? ORDER BY timestamp DESC LIMIT ?",
            (object_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def add_audit_event(event: dict) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO audit_events "
            "(id, actor, timestamp, action, object_id, result) VALUES (?, ?, ?, ?, ?, ?)",
            (
                event["id"], event["actor"], event["timestamp"],
                event["action"], event["objectId"], event["result"],
            ),
        )


def count_audit_events() -> int:
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM audit_events").fetchone()["n"]
