"""
Pagination helper
-------------------
Two patterns are supported:

1. `paginate_with_headers` — non-breaking: the response body stays a plain
   list (matching every existing frontend call), total count goes in an
   `X-Total-Count` response header. Used to retrofit pagination onto
   endpoints whose frontend consumers already expect an array back, without
   risking a shape change that couldn't be runtime-verified against the
   frontend in this sandbox.
2. `paginate` — returns (items, total) directly for new endpoints that can
   choose their own response shape from the start.

Default page_size is 200 (not a smaller "best practice" number like 25-50)
specifically because several existing frontend pages currently fetch a
list once and compute aggregates (totals, averages) against the full set
client-side. A small default would silently truncate those pages' data.
200 comfortably covers this project's seed-data scale without being
truly unbounded.
"""
from typing import TypeVar
from fastapi import Query, Response
from sqlalchemy.orm import Query as SAQuery

T = TypeVar("T")


class Pagination:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(200, ge=1, le=500)):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def paginate(query: SAQuery, pagination: "Pagination") -> tuple[list, int]:
    total = query.order_by(None).count()  # order_by(None) avoids ORDER BY slowing down a pure COUNT
    items = query.offset(pagination.offset).limit(pagination.page_size).all()
    return items, total


def paginate_with_headers(query: SAQuery, pagination: "Pagination", response: Response) -> list:
    items, total = paginate(query, pagination)
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page"] = str(pagination.page)
    response.headers["X-Page-Size"] = str(pagination.page_size)
    return items
