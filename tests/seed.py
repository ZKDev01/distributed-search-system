import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SERVER_URL = "http://127.0.0.1:8000"


FILES = [
    {
        "file_id": "f1",
        "name": "manual_inicio.txt",
        "path": str(ROOT / "samples" / "manual_inicio.txt"),
        "mime_type": "text/plain",
        "size": 1200,
        "last_modified": 1699999999,
        "indexed_at": 1699999999,
    },
    {
        "file_id": "f2",
        "name": "guia_rapida.pdf",
        "path": str(ROOT / "samples" / "guia_rapida.pdf"),
        "mime_type": "application/pdf",
        "size": 512000,
        "last_modified": 1699999999,
        "indexed_at": 1699999999,
    },
]


def main():
    for f in FILES:
        r = requests.post(f"{SERVER_URL}/files", json=f, timeout=10)
        r.raise_for_status()
        print("inserted:", f["file_id"], f["name"])

    r = requests.get(f"{SERVER_URL}/search", params={"q": "manual"}, timeout=10)
    r.raise_for_status()
    print("search results:", r.json())


if __name__ == "__main__":
    main()
