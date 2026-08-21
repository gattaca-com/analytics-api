from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import TransactionSourcePage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/transaction-sources", tags=["transaction-sources"])

COLUMNS = (
    "ts.timestamp, ts.hash, ts.entry_point_id, ep.entry_point AS entry_point, "
    "ts.source_id, src.source AS source, ts.region_id, rg.region AS region, "
    "ts.bundle_hash "
    "FROM orderflow.transaction_source ts "
    "LEFT JOIN label.entry_point ep ON ep.id = ts.entry_point_id "
    "LEFT JOIN label.source src ON src.id = ts.source_id "
    "LEFT JOIN label.region rg ON rg.id = ts.region_id"
)


@router.get(
    "",
    response_model=TransactionSourcePage,
    summary="List / look up transaction orderflow sources",
)
async def list_transaction_sources(
    hash: str | None = Query(None, description="Transaction hash (0x-hex)."),
    bundle: str | None = Query(None, description="Bundle hash (0x-hex)."),
    start: datetime | None = Query(None, description="Range start (inclusive)."),
    end: datetime | None = Query(None, description="Range end (exclusive)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `hash`, `bundle`, or a `start`/`end` range.

    Range filters on `timestamp`.
    """
    validate_range(start, end)
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (hash, bundle, start))
    if selectors != 1:
        raise HTTPException(422, "provide exactly one of: hash, bundle, or start+end")

    if hash is not None:
        where.append(f"ts.hash = ${len(args) + 1}")
        args.append(hex_to_bytes(hash))
    elif bundle is not None:
        where.append(f"ts.bundle_hash = ${len(args) + 1}")
        args.append(hex_to_bytes(bundle))
    else:
        where.append(f"ts.timestamp >= ${len(args) + 1}")
        args.append(start)
        where.append(f"ts.timestamp < ${len(args) + 1}")
        args.append(end)

    return await run_page(COLUMNS, where, args, "ts.timestamp DESC", page)
