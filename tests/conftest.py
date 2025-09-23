from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "doc-search-mvp" / "server"
sys.path.insert(0, str(SERVER_DIR))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Import db first so we can override DB_PATH before app startup runs
    import db  # type: ignore

    test_db_path = tmp_path / "test_doc_search.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path, raising=False)

    # Now import app and initialize schema via startup when TestClient starts
    import main  # type: ignore

    with TestClient(main.app) as tc:
        yield tc
