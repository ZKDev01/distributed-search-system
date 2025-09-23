from typing import Any


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_upsert_search_delete_flow(client):
    # Upsert a file
    payload = {
        "file_id": "f1",
        "name": "manual_de_usuario.txt",
        "path": "C:/docs/manual_de_usuario.txt",
        "mime_type": "text/plain",
        "size": 3210,
        "last_modified": 1699999999,
        "indexed_at": 1699999999,
    }
    r = client.post("/files", json=payload)
    assert r.status_code == 200

    # Search it
    r = client.get("/search", params={"q": "manual"})
    assert r.status_code == 200
    data: dict[str, Any] = r.json()
    assert data["count"] >= 1
    assert any(item["file_id"] == "f1" for item in data["items"])

    # Delete it
    r = client.delete("/files/f1")
    assert r.status_code == 200

    # Ensure it's gone in subsequent search
    r = client.get("/search", params={"q": "manual"})
    data = r.json()
    assert all(item["file_id"] != "f1" for item in data["items"])
