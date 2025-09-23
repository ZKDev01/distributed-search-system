from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional, List

from db import init_db, upsert_file, delete_file as db_delete_file, search_by_name


app = FastAPI(title="Doc Search MVP")


@app.on_event("startup")
async def startup_event():
    # Initialize database schema
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


class FileIn(BaseModel):
    file_id: str
    name: str
    path: str
    mime_type: Optional[str] = None
    size: Optional[int] = None
    last_modified: Optional[int] = None
    indexed_at: Optional[int] = None


@app.post("/files")
def upsert_file_endpoint(payload: FileIn):
    upsert_file(
        file_id=payload.file_id,
        name=payload.name,
        path=payload.path,
        mime_type=payload.mime_type,
        size=payload.size,
        last_modified=payload.last_modified,
        indexed_at=payload.indexed_at,
    )
    return {"status": "ok"}


@app.delete("/files/{file_id}")
def delete_file_endpoint(file_id: str):
    db_delete_file(file_id=file_id)
    return {"status": "ok"}


@app.get("/search")
def search_endpoint(
    q: str = Query("", min_length=0), limit: int = Query(20, ge=1, le=200)
):
    results = search_by_name(q, limit=limit) if q else []
    return {"items": results, "count": len(results)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
