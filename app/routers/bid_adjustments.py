from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import BidAdjustmentPage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/bid-adjustments", tags=["bid-adjustments"])

COLUMNS = (
    "ba.relay_id, r.relay AS relay, ba.slot_number, ba.block_number, "
    "ba.adjusted_block_hash, ba.adjusted_value, ba.builder_pubkey_id, "
    "bp.pubkey AS builder_pubkey, bp.extra_data AS builder_extra_data, "
    "ba.delta, ba.fee, ba.submitted_block_hash, ba.submitted_received_at, "
    "ba.submitted_value "
    "FROM relay.bid_adjustment ba "
    "LEFT JOIN label.relay r ON r.id = ba.relay_id "
    "LEFT JOIN label.builder_pubkey bp ON bp.id = ba.builder_pubkey_id"
)


@router.get(
    "", response_model=BidAdjustmentPage, summary="List / look up relay bid adjustments"
)
async def list_bid_adjustments(
    slot: int | None = Query(None, description="Exact slot_number."),
    block: int | None = Query(None, description="Exact block number."),
    hash: str | None = Query(
        None, description="Match submitted OR adjusted block hash (0x-hex)."
    ),
    start: datetime | None = Query(None, description="Range start (inclusive)."),
    end: datetime | None = Query(None, description="Range end (exclusive)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `slot`, `block`, `hash`, or a `start`/`end` range.

    Range filters on `submitted_received_at`.
    """
    validate_range(start, end)
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (slot, block, hash, start))
    if selectors != 1:
        raise HTTPException(
            422, "provide exactly one of: slot, block, hash, or start+end"
        )

    if slot is not None:
        where.append(f"ba.slot_number = ${len(args) + 1}")
        args.append(slot)
    elif block is not None:
        where.append(f"ba.block_number = ${len(args) + 1}")
        args.append(block)
    elif hash is not None:
        h = hex_to_bytes(hash)
        where.append(
            f"(ba.submitted_block_hash = ${len(args) + 1} "
            f"OR ba.adjusted_block_hash = ${len(args) + 1})"
        )
        args.append(h)
    else:
        where.append(f"ba.submitted_received_at >= ${len(args) + 1}")
        args.append(start)
        where.append(f"ba.submitted_received_at < ${len(args) + 1}")
        args.append(end)

    return await run_page(
        COLUMNS, where, args, "ba.submitted_received_at DESC", page
    )
