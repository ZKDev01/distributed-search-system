"""
Simple indexer placeholder. In the future, implement functions to scan a directory,
extract text from documents, and store embeddings/metadata in the DB.
"""

from typing import List


def index_documents(paths: List[str]) -> int:
    """Pretend to index documents and return the count indexed."""
    # TODO: Implement real indexing
    return len(paths)
