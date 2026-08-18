from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import TransactionPage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/transactions", tags=["transactions"])

COLUMNS = (
    "hash, block_number, timestamp, index, success, to_address, from_address, "
    "type, gas_used, priority_fee_per_gas, priority_fee, internal_transfer_fee, "
    "kickback, value, merge_contributor FROM mined.transaction"
)


@router.get(
    "", response_model=TransactionPage, summary="List / look up mined transactions"
)
async def list_transactions(
    hash: str | None = Query(None, description="Transaction hash (0x-hex)."),
    block: int | None = Query(None, description="Exact block number."),
    start: datetime | None = Query(None, description="Range start (inclusive)."),
    end: datetime | None = Query(None, description="Range end (exclusive)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `hash`, `block`, or a `start`/`end` range."""
    validate_range(start, end)
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (hash, block, start))
    if selectors != 1:
        raise HTTPException(
            422, "provide exactly one of: hash, block, or start+end"
        )

    if hash is not None:
        where.append(f"hash = ${len(args) + 1}")
        args.append(hex_to_bytes(hash))
    elif block is not None:
        where.append(f"block_number = ${len(args) + 1}")
        args.append(block)
    else:
        where.append(f"timestamp >= ${len(args) + 1}")
        args.append(start)
        where.append(f"timestamp < ${len(args) + 1}")
        args.append(end)

    return await run_page(COLUMNS, where, args, "timestamp DESC, index ASC", page)
