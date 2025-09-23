-- Schema for Doc Search MVP (files + optional FTS5 on name)

CREATE TABLE IF NOT EXISTS files (
    file_id TEXT PRIMARY KEY,
    name TEXT,
    path TEXT,
    mime_type TEXT,
    size INTEGER,
    last_modified INTEGER,
    indexed_at INTEGER
);

-- FTS5 virtual table (optional, may fail if SQLite lacks FTS5)
-- Note: this statement may fail at runtime on environments without FTS5.
-- In that case, the app should fall back to LIKE searches.
CREATE VIRTUAL TABLE IF NOT EXISTS fts_name USING fts5(name, file_id UNINDEXED);
