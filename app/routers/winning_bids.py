from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import WinningBidPage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/winning-bids", tags=["winning-bids"])

COLUMNS = (
    "wb.slot_number, wb.winning_timestamp, wb.winning_relay_id, "
    "r.relay AS relay, wb.block_hash, wb.winning_bid_value, "
    "wb.other_relay_ids, wb.block_uuid, wb.is_passthrough "
    "FROM relay.winning_bid wb "
    "LEFT JOIN label.relay r ON r.id = wb.winning_relay_id"
)


@router.get("", response_model=WinningBidPage, summary="List / look up winning relay bids")
async def list_winning_bids(
    slot: int | None = Query(None, description="Exact slot_number."),
    hash: str | None = Query(None, description="Block hash (0x-hex)."),
    start: datetime | None = Query(None, description="Range start (inclusive)."),
    end: datetime | None = Query(None, description="Range end (exclusive)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `slot`, `hash`, or a `start`/`end` range.

    Range filters on `winning_timestamp`.
    """
    validate_range(start, end)
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (slot, hash, start))
    if selectors != 1:
        raise HTTPException(422, "provide exactly one of: slot, hash, or start+end")

    if slot is not None:
        where.append(f"wb.slot_number = ${len(args) + 1}")
        args.append(slot)
    elif hash is not None:
        where.append(f"wb.block_hash = ${len(args) + 1}")
        args.append(hex_to_bytes(hash))
    else:
        where.append(f"wb.winning_timestamp >= ${len(args) + 1}")
        args.append(start)
        where.append(f"wb.winning_timestamp < ${len(args) + 1}")
        args.append(end)

    return await run_page(COLUMNS, where, args, "wb.winning_timestamp DESC", page)
