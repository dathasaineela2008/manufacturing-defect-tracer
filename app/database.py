"""
Database access layer.

Uses parameterized queries only (never string-concatenated SQL).
Supports MySQL (college DBMS requirement) and SQLite (local/tests).
Credentials come from environment variables, not from source code.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


class DatabaseError(Exception):
    """Friendly wrapper around low-level database failures."""


def _engine() -> str:
    return os.getenv("DB_ENGINE", "mysql").strip().lower()


def mysql_config() -> Dict[str, Any]:
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "mdtps"),
        "charset": "utf8mb4",
        "cursorclass": None,
        "autocommit": False,
    }


class DatabaseManager:
    """Tiny data-access object used by the rest of the application."""

    def __init__(self) -> None:
        self.engine = _engine()
        if self.engine not in {"mysql", "sqlite"}:
            raise DatabaseError("DB_ENGINE must be 'mysql' or 'sqlite'.")

    @property
    def placeholder(self) -> str:
        return "%s" if self.engine == "mysql" else "?"

    def _connect(self):
        try:
            if self.engine == "mysql":
                import pymysql
                from pymysql.cursors import DictCursor

                cfg = mysql_config()
                cfg["cursorclass"] = DictCursor
                return pymysql.connect(**cfg)

            if os.getenv("VERCEL"):
                tmp_db = Path("/tmp/mdtps.sqlite3")
                if not tmp_db.exists():
                    src_db = ROOT / "instance" / "mdtps.sqlite3"
                    if src_db.exists():
                        import shutil
                        shutil.copy2(src_db, tmp_db)
                    else:
                        from app.seed import seed_sqlite
                        # Seed fresh database directly in /tmp
                        conn = sqlite3.connect(str(tmp_db))
                        conn.row_factory = sqlite3.Row
                        conn.execute("PRAGMA foreign_keys = ON")
                        from app.seed import seed_sqlite_conn
                        seed_sqlite_conn(conn)
                        return conn
                sqlite_path = tmp_db
            else:
                sqlite_path = Path(os.getenv("SQLITE_PATH", "instance/mdtps.sqlite3"))
                if not sqlite_path.is_absolute():
                    sqlite_path = ROOT / sqlite_path
                sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(sqlite_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as exc:  # noqa: BLE001 - convert to friendly error
            raise DatabaseError(
                "Could not connect to the database. Check .env settings and "
                "confirm that MySQL is running (or switch DB_ENGINE=sqlite)."
            ) from exc

    @contextmanager
    def connection(self):
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def query(self, sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            if self.engine == "sqlite":
                return [dict(row) for row in rows]
            return list(rows)

    def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.rowcount

    def execute_many(self, sql: str, rows: Iterable[Sequence[Any]]) -> None:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(sql, list(rows))

    def query_one(self, sql: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
        rows = self.query(sql, params)
        return rows[0] if rows else None


db = DatabaseManager()
