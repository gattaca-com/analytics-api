from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import BlockPage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/blocks", tags=["blocks"])

COLUMNS = (
    "b.number, b.timestamp, b.slot_number, b.hash, b.gas_used, b.gas_limit, "
    "b.base_fee_per_gas, b.extra_data, b.builder, "
    "b.proposer, lp.name AS proposer_name, "
    "b.transaction_fees, b.burnt_fees, b.internal_transfer_fees, "
    "b.builder_payment, b.proposer_payment"
    "FROM mined.block b "
    "LEFT JOIN label.address lp ON lp.address = b.proposer"
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
        where.append(f"b.slot_number = ${len(args) + 1}")
        args.append(slot)
    elif block is not None:
        where.append(f"b.number = ${len(args) + 1}")
        args.append(block)
    elif hash is not None:
        where.append(f"b.hash = ${len(args) + 1}")
        args.append(hex_to_bytes(hash))
    else:
        where.append(f"b.timestamp >= ${len(args) + 1}")
        args.append(start)
        where.append(f"b.timestamp < ${len(args) + 1}")
        args.append(end)

    return await run_page(COLUMNS, where, args, "b.number DESC", page)
