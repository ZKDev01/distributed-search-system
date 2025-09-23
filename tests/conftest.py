import os
import tempfile
import shutil
import contextlib
import threading
import time

import pytest
import uvicorn

# Ensure server package imports resolve
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "doc-search-mvp" / "server"
sys.path.insert(0, str(SERVER_DIR))

from main import app  # noqa: E402
from db import DB_PATH  # noqa: E402


@contextlib.contextmanager
def temporary_db():
    # Use a temp dir for DB file
    tmpdir = tempfile.mkdtemp(prefix="docsearch_test_")
    try:
        env_var = "DOCSEARCH_DB_PATH"
        # Override DB_PATH via env var if implemented; otherwise monkeypatch Path
        # For simplicity in this MVP, we move the DB file path by chdir
        # NOTE: In production, db.py should read a configurable path.
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            yield Path(tmpdir)
        finally:
            os.chdir(cwd)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture(scope="session")
def test_server():
    # Run uvicorn in a background thread using an ephemeral port
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait a bit for startup
    time.sleep(0.8)
    # Discover the port (uvicorn stores sockets in server.servers)
    # Since this is a minimal setup, we assume default 8000 if not exposed
    port = 8000
    base_url = f"http://127.0.0.1:{port}"

    yield base_url

    # Stopping server (best-effort)
    if server and server.started:
        server.should_exit = True
        thread.join(timeout=2)
