"""
Persistent scan-history storage.

Scan summaries are stored in a SQLite database so that history survives
across process invocations (``nmap-ai history`` in a fresh process can see
scans run earlier). The database location is taken from
``DatabaseConfig.url`` (a SQLAlchemy-style ``sqlite:///`` URL); only SQLite
URLs are supported and they are handled with the stdlib ``sqlite3`` module
to avoid a heavyweight ORM dependency.
"""

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger


def sqlite_url_to_path(url: str) -> str:
    """Convert a ``sqlite:///`` URL to a filesystem path (or ``:memory:``).

    Examples:
        ``sqlite:///history.db``   -> ``history.db``   (relative)
        ``sqlite:////tmp/h.db``    -> ``/tmp/h.db``    (absolute)
        ``sqlite:///:memory:``     -> ``:memory:``
        ``/already/a/path.db``     -> ``/already/a/path.db``
    """
    for prefix in ("sqlite:///", "sqlite://"):
        if url.startswith(prefix):
            return url[len(prefix):]
    return url


class ScanHistoryStore:
    """SQLite-backed store for scan summaries."""

    def __init__(self, db_url: str = "sqlite:///nmap_ai.db"):
        self.logger = get_logger(__name__)
        self.db_path = sqlite_url_to_path(db_url)

        if self.db_path not in (":memory:", ""):
            parent = Path(self.db_path).expanduser().parent
            if str(parent) and parent != Path("."):
                parent.mkdir(parents=True, exist_ok=True)
            self.db_path = str(Path(self.db_path).expanduser())

        # A single connection shared across threads (async scans run in a
        # thread pool); guarded by a lock since sqlite3 connections are not
        # safe for concurrent use.
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration REAL,
                    targets TEXT,
                    ports TEXT,
                    arguments TEXT,
                    ai_enabled INTEGER,
                    summary TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._conn.commit()

    def save(self, summary: Dict[str, Any]) -> None:
        """Persist a single scan summary."""
        targets = summary.get("targets", [])
        payload = json.dumps(summary, default=str)
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO scan_history
                    (scan_id, start_time, end_time, duration, targets,
                     ports, arguments, ai_enabled, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.get("scan_id"),
                    summary.get("start_time"),
                    summary.get("end_time"),
                    summary.get("duration"),
                    json.dumps(targets, default=str),
                    summary.get("ports"),
                    summary.get("arguments"),
                    1 if summary.get("ai_enabled") else 0,
                    payload,
                ),
            )
            self._conn.commit()

    def get(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return stored scan summaries oldest-first.

        When ``limit`` is given, return the ``limit`` most recent scans
        (still in chronological order).
        """
        with self._lock:
            if limit is not None:
                rows = self._conn.execute(
                    "SELECT summary FROM scan_history ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
                rows = list(reversed(rows))
            else:
                rows = self._conn.execute(
                    "SELECT summary FROM scan_history ORDER BY id ASC"
                ).fetchall()

        summaries: List[Dict[str, Any]] = []
        for row in rows:
            try:
                summaries.append(json.loads(row["summary"]))
            except (json.JSONDecodeError, TypeError):
                self.logger.warning("Skipping unreadable scan_history row")
        return summaries

    def count(self) -> int:
        with self._lock:
            return self._conn.execute(
                "SELECT COUNT(*) FROM scan_history"
            ).fetchone()[0]

    def clear(self) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM scan_history")
            self._conn.commit()

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

    def __del__(self):
        self.close()
