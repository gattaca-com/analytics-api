from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import BlockPage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/blocks", tags=["blocks"])

COLUMNS = (
    "number, timestamp, slot_number, hash, gas_used, gas_limit, "
    "base_fee_per_gas, size, extra_data, builder, proposer, transaction_fees, "
    "burnt_fees, internal_transfer_fees, builder_payment, proposer_payment, "
    "blob_count, injected_subsidy_fee FROM mined.block"
)


@router.get("", response_model=BlockPage, summary="List / look up mined blocks")
async def list_blocks(
    slot: int | None = Query(None, description="Exact slot_number."),
    block: int | None = Query(None, description="Exact block number."),
    hash: str | None = Query(None, description="Block hash (0x-hex)."),
    start: datetime | None = Query(None, description="Range start (inclusive)."),
    end: datetime | None = Query(None, description="Range end (exclusive)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `slot`, `block`, `hash`, or a `start`/`end` range."""
    validate_range(start, end)
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (slot, block, hash, start))
    if selectors != 1:
        raise HTTPException(
            422, "provide exactly one of: slot, block, hash, or start+end"
        )

    if slot is not None:
        where.append(f"slot_number = ${len(args) + 1}")
        args.append(slot)
    elif block is not None:
        where.append(f"number = ${len(args) + 1}")
        args.append(block)
    elif hash is not None:
        where.append(f"hash = ${len(args) + 1}")
        args.append(hex_to_bytes(hash))
    else:
        where.append(f"timestamp >= ${len(args) + 1}")
        args.append(start)
        where.append(f"timestamp < ${len(args) + 1}")
        args.append(end)

    return await run_page(COLUMNS, where, args, "number DESC", page)
