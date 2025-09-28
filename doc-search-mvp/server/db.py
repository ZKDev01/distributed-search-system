"""SQLite helper for Doc Search MVP"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Permitir configurar la ruta de la DB por variable de entorno (útil en Docker)
_db_from_env = os.getenv("DOCSEARCH_DB_PATH")
DB_PATH = (
    Path(_db_from_env) if _db_from_env else Path(__file__).with_name("doc_search.db")
)


@contextmanager
def get_conn():
    # Ensure parent directory exists (no-op if same dir)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Open connection (use str for compatibility); tune args if needed
    conn = sqlite3.connect(str(DB_PATH), timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        # Commit only if no exception occurred in caller
        conn.commit()
    except Exception:
        # Roll back if something failed, then re-raise
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database schema from schema.sql.

    Attempts to create optional FTS5 table; if it fails, continues without it.
    """
    schema_path = Path(__file__).with_name("schema.sql")
    with get_conn() as conn:
        sql = schema_path.read_text(encoding="utf-8")
        cur = conn.cursor()
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            try:
                cur.execute(stmt)
            except sqlite3.OperationalError as e:
                # If FTS5 is unavailable, ignore the virtual table creation
                if "fts5" in stmt.lower():
                    # log-like comment; in real app use logging
                    # print(f"FTS5 unavailable: {e}")
                    continue
                raise


def upsert_file(
    *,
    file_id: str,
    name: str,
    path: str,
    mime_type: str | None,
    size: int | None,
    last_modified: int | None,
    indexed_at: int | None,
) -> None:
    """Insert or update a file row and sync FTS if available."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO files (file_id, name, path, mime_type, size, last_modified, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_id) DO UPDATE SET
              name=excluded.name,
              path=excluded.path,
              mime_type=excluded.mime_type,
              size=excluded.size,
              last_modified=excluded.last_modified,
              indexed_at=excluded.indexed_at
            """,
            (file_id, name, path, mime_type, size, last_modified, indexed_at),
        )

        # Try to keep FTS in sync; ignore if table not present
        try:
            # obtain rowid for this file and do delete-then-insert to refresh FTS
            cur.execute("SELECT rowid FROM files WHERE file_id=?", (file_id,))
            r = cur.fetchone()
            if r is not None:
                rowid = r[0]
                cur.execute("DELETE FROM fts_name WHERE rowid=?", (rowid,))
                cur.execute(
                    "INSERT INTO fts_name(rowid, name, file_id) VALUES (?, ?, ?)",
                    (rowid, name, file_id),
                )
        except sqlite3.OperationalError:
            pass


def delete_file(*, file_id: str) -> None:
    """Delete a file row and remove from FTS if present."""
    with get_conn() as conn:
        cur = conn.cursor()
        # delete from base table; capture rowid before delete to clean FTS
        cur.execute("SELECT rowid FROM files WHERE file_id=?", (file_id,))
        row = cur.fetchone()
        cur.execute("DELETE FROM files WHERE file_id=?", (file_id,))

        if row is not None:
            rowid = row[0]
            try:
                cur.execute("DELETE FROM fts_name WHERE rowid=?", (rowid,))
            except sqlite3.OperationalError:
                pass


def search_by_name(query: str, limit: int = 20) -> list[dict]:
    """Search files by name using FTS5 if available; fallback to LIKE.

    Returns list of dicts with columns from `files`.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        # Try FTS5 first
        try:
            cur.execute(
                """
                SELECT f.* FROM fts_name fn
                JOIN files f ON f.rowid = fn.rowid
                WHERE fn.name MATCH ?
                LIMIT ?
                """,
                (query, limit),
            )
            rows = cur.fetchall()
        except sqlite3.OperationalError:
            # Fallback to LIKE search
            cur.execute(
                "SELECT * FROM files WHERE name LIKE ? ORDER BY name LIMIT ?",
                (f"%{query}%", limit),
            )
            rows = cur.fetchall()

        return [dict(row) for row in rows]
