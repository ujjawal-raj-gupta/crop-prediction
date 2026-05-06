from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = PROJECT_ROOT / "smart_crop.db"


def get_db_path() -> Path:
    # Allow overriding for cloud deployments
    p = (os.getenv("DATABASE_PATH") or "").strip()
    return Path(p) if p else DEFAULT_DB_PATH


@contextmanager
def connect():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sms_jobs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at_utc TEXT NOT NULL,
              to_number TEXT NOT NULL,
              crop TEXT NOT NULL,
              when_utc TEXT NOT NULL,
              body TEXT NOT NULL,
              sent_at_utc TEXT NULL,
              status TEXT NOT NULL DEFAULT 'pending',
              last_error TEXT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sms_jobs_pending_when ON sms_jobs(status, when_utc)")


def enqueue_sms_jobs(*, to_number: str, crop: str, jobs: list[dict]) -> int:
    """
    jobs: [{when_utc: iso, body: str}]
    Returns number of inserted jobs.
    """
    with connect() as conn:
        cur = conn.cursor()
        cur.executemany(
            """
            INSERT INTO sms_jobs(created_at_utc, to_number, crop, when_utc, body, status)
            VALUES(datetime('now'), ?, ?, ?, ?, 'pending')
            """,
            [(to_number, crop, j["when_utc"], j["body"]) for j in jobs],
        )
        return cur.rowcount


def fetch_due_pending_jobs(*, limit: int = 25) -> list[sqlite3.Row]:
    with connect() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM sms_jobs
            WHERE status = 'pending'
              AND when_utc <= datetime('now')
            ORDER BY when_utc ASC
            LIMIT ?
            """,
            (limit,),
        )
        return list(cur.fetchall())


def mark_job_sent(*, job_id: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE sms_jobs SET status='sent', sent_at_utc=datetime('now'), last_error=NULL WHERE id=?",
            (job_id,),
        )


def mark_job_failed(*, job_id: int, error: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE sms_jobs SET status='failed', last_error=? WHERE id=?",
            (error[:2000], job_id),
        )


def list_recent_jobs(*, to_number: str, limit: int = 10) -> list[sqlite3.Row]:
    with connect() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM sms_jobs
            WHERE to_number = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (to_number, limit),
        )
        return list(cur.fetchall())

