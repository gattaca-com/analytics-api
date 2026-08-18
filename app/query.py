from typing import Any

from fastapi import HTTPException

from app.db import fetch
from app.pagination import PageParams, Pagination
from app.serializers import row_to_dict


def hex_to_bytes(value: str) -> bytes:
    try:
        return bytes.fromhex(value[2:] if value.startswith("0x") else value)
    except ValueError:
        raise HTTPException(422, f"invalid hex value: {value!r}")


async def run_page(
    select_from: str,
    where: list[str],
    args: list[Any],
    order_by: str,
    page: PageParams,
) -> dict[str, Any]:
    """Run a paginated SELECT. Fetches limit+1 rows to derive has_more."""
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    args = list(args)
    limit_pos = len(args) + 1
    offset_pos = len(args) + 2
    args.extend([page.limit + 1, page.offset])
    sql = (
        f"SELECT {select_from} {where_sql} ORDER BY {order_by} "
        f"LIMIT ${limit_pos} OFFSET ${offset_pos}"
    )
    rows = await fetch(sql, *args)
    has_more = len(rows) > page.limit
    rows = rows[: page.limit]
    data = [row_to_dict(r) for r in rows]
    return {
        "data": data,
        "pagination": Pagination(
            limit=page.limit,
            offset=page.offset,
            count=len(data),
            has_more=has_more,
        ),
    }
