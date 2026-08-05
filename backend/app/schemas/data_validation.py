from typing import Any
from pydantic import BaseModel


class CommitRequest(BaseModel):
    dataset_type: str
    rows: list[dict[str, Any]]


class CommitResult(BaseModel):
    dataset_type: str
    inserted: int
    skipped: int
    errors: list[str] = []
