from datetime import datetime

from fastapi import HTTPException, Query
from pydantic import BaseModel

from app.config import settings


class PageParams:
    def __init__(
        self,
        limit: int = Query(
            settings.default_limit, ge=1, description="Max rows to return."
        ),
        offset: int = Query(0, ge=0, description="Rows to skip."),
    ):
        if limit > settings.max_limit:
            raise HTTPException(
                422, f"limit exceeds maximum of {settings.max_limit}"
            )
        self.limit = limit
        self.offset = offset


class Pagination(BaseModel):
    limit: int
    offset: int
    count: int
    has_more: bool


def validate_range(
    start: datetime | None,
    end: datetime | None,
    max_seconds: int | None = None,
) -> None:
    if (start is None) != (end is None):
        raise HTTPException(422, "start and end must be provided together")
    if start is not None and end is not None:
        if end <= start:
            raise HTTPException(422, "end must be after start")
        cap = max_seconds if max_seconds is not None else settings.max_range_seconds
        width = (end - start).total_seconds()
        if width > cap:
            raise HTTPException(
                422,
                f"time range too wide: {width:.0f}s > max {cap}s",
            )
