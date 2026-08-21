from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import settings
from app.models import BidSubmissionPage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/bid-submissions", tags=["bid-submissions"])

COLUMNS = (
    "bs.relay_id, r.relay AS relay, bs.slot_number, bs.block_number, "
    "bs.block_hash, bs.builder_pubkey_id, bp.pubkey AS builder_pubkey, "
    "bp.extra_data AS builder_extra_data, bs.value, bs.timestamp "
    "FROM relay.bid_submission bs "
    "LEFT JOIN label.relay r ON r.id = bs.relay_id "
    "LEFT JOIN label.builder_pubkey bp ON bp.id = bs.builder_pubkey_id"
)

GENESIS = datetime(2020, 12, 1, 12, 0, 23, tzinfo=timezone.utc)


def _slot_window(slot: int) -> tuple[datetime, datetime]:
    """Bids for a slot arrive around its 12s wall-clock window; a generous
    margin lets TimescaleDB prune chunks instead of walking the whole
    timestamp index."""
    slot_start = GENESIS + timedelta(seconds=slot * 12)
    return slot_start - timedelta(seconds=120), slot_start + timedelta(seconds=60)


@router.get(
    "", response_model=BidSubmissionPage, summary="List / look up relay bid submissions"
)
async def list_bid_submissions(
    slot: int | None = Query(None, description="Exact slot_number."),
    hash: str | None = Query(None, description="Block hash (0x-hex)."),
    start: datetime | None = Query(None, description="Range start (inclusive)."),
    end: datetime | None = Query(None, description="Range end (exclusive)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `slot`, `hash`, or a `start`/`end` range.

    This is a very large hypertable, so ranges are capped tighter than other
    endpoints (`BID_SUBMISSION_MAX_RANGE_SECONDS`, default 1h). Range filters
    on `timestamp`.
    """
    validate_range(start, end, max_seconds=settings.bid_submission_max_range_seconds)
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (slot, hash, start))
    if selectors != 1:
        raise HTTPException(422, "provide exactly one of: slot, hash, or start+end")

    if slot is not None:
        where.append(f"bs.slot_number = ${len(args) + 1}")
        args.append(slot)
        lo, hi = _slot_window(slot)
        where.append(f"bs.timestamp >= ${len(args) + 1}")
        args.append(lo)
        where.append(f"bs.timestamp < ${len(args) + 1}")
        args.append(hi)
    elif hash is not None:
        where.append(f"bs.block_hash = ${len(args) + 1}")
        args.append(hex_to_bytes(hash))
    else:
        where.append(f"bs.timestamp >= ${len(args) + 1}")
        args.append(start)
        where.append(f"bs.timestamp < ${len(args) + 1}")
        args.append(end)

    return await run_page(COLUMNS, where, args, "bs.timestamp DESC", page)
