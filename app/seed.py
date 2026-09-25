"""Load schema + sample data and create the hashed demo administrator."""

from __future__ import annotations

import os
from pathlib import Path

from werkzeug.security import generate_password_hash

from app.database import DatabaseManager, mysql_config

ROOT = Path(__file__).resolve().parent.parent
DEMO_USERNAME = "admin"
DEMO_PASSWORD = "Admin@123"


def _split_sql(text: str) -> list[str]:
    statements = []
    current = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("--"):
            continue
        current.append(raw)
        if line.endswith(";"):
            stmt = "\n".join(current).strip().rstrip(";")
            current = []
            if stmt:
                statements.append(stmt)
    return statements


def _mysql_server_connection():
    import pymysql

    cfg = mysql_config()
    cfg.pop("database", None)
    cfg.pop("cursorclass", None)
    return pymysql.connect(**cfg)


def seed_mysql() -> None:
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    sample = (ROOT / "database" / "sample_data.sql").read_text(encoding="utf-8")
    conn = _mysql_server_connection()
    try:
        cursor = conn.cursor()
        for stmt in _split_sql(schema):
            cursor.execute(stmt)
        conn.select_db(os.getenv("MYSQL_DATABASE", "mdtps"))
        for stmt in _split_sql(sample):
            if stmt.upper().startswith("USE "):
                continue
            cursor.execute(stmt)
        _ensure_demo_user_mysql(cursor)
        conn.commit()
    finally:
        conn.close()


def _ensure_demo_user_mysql(cursor) -> None:
    cursor.execute("SELECT user_id FROM app_user WHERE username=%s", (DEMO_USERNAME,))
    if cursor.fetchone():
        return
    cursor.execute(
        "INSERT INTO app_user (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
        (DEMO_USERNAME, generate_password_hash(DEMO_PASSWORD), "Academic Demo Administrator", "ADMIN"),
    )


def seed_sqlite_conn(conn) -> None:
    schema = (ROOT / "database" / "schema_sqlite.sql").read_text(encoding="utf-8")
    sample = (ROOT / "database" / "sample_data.sql").read_text(encoding="utf-8")
    cursor = conn.cursor()
    cursor.executescript(schema)
    for stmt in _split_sql(sample):
        upper = stmt.upper()
        if upper.startswith("USE ") or "FOREIGN_KEY_CHECKS" in upper:
            continue
        if upper.startswith("DELETE FROM"):
            cursor.execute(stmt)
            continue
        if upper.startswith("INSERT INTO"):
            cursor.execute(stmt)
    cursor.execute("SELECT user_id FROM app_user WHERE username = ?", (DEMO_USERNAME,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO app_user (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (DEMO_USERNAME, generate_password_hash(DEMO_PASSWORD), "Academic Demo Administrator", "ADMIN"),
        )
    conn.commit()


def seed_sqlite(db: DatabaseManager) -> None:
    with db.connection() as conn:
        seed_sqlite_conn(conn)


def seed_all() -> str:
    db = DatabaseManager()
    if db.engine == "mysql":
        seed_mysql()
        return "MySQL database mdtps seeded."
    seed_sqlite(db)
    return "SQLite database seeded."


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    print(seed_all())
