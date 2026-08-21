from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import SubmittedBlockPage
from app.pagination import PageParams, validate_range
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/submitted-blocks", tags=["submitted-blocks"])

COLUMNS = (
    "sb.uuid, sb.builder_id, b.builder AS builder, sb.strategy_id, "
    "s.strategy AS strategy, sb.slot_number, sb.builder_payment, "
    "sb.raw_builder_payment, sb.gas_used, sb.on_build_start, "
    "sb.on_build_finish, sb.submission_ts, sb.orders_count, "
    "sb.bundles_count, sb.eob_bundles, sb.blobs_count, sb.sim_time, "
    "sb.block_type AS block_type_id, bt.block_type AS block_type, "
    "sb.removed_ts, sb.removed_reason AS removed_reason_id, "
    "rr.reason AS removed_reason, sb.removed_triggering_block, "
    "sb.eob_value, sb.cex_dex_value, sb.best_order_value "
    "FROM builder.submitted_block sb "
    "LEFT JOIN label.builder b ON b.id = sb.builder_id "
    "LEFT JOIN label.strategy s ON s.id = sb.strategy_id "
    "LEFT JOIN label.block_type bt ON bt.id = sb.block_type "
    "LEFT JOIN label.block_rejection_reason rr ON rr.id = sb.removed_reason"
)


@router.get(
    "",
    response_model=SubmittedBlockPage,
    summary="List / look up Titan builder submitted blocks",
)
async def list_submitted_blocks(
    slot: int | None = Query(None, description="Exact slot_number."),
    uuid: str | None = Query(None, description="Block UUID (0x-hex)."),
    start: datetime | None = Query(None, description="Range start (inclusive)."),
    end: datetime | None = Query(None, description="Range end (exclusive)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `slot`, `uuid`, or a `start`/`end` range.

    Range filters on `submission_ts`.
    """
    validate_range(start, end)
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (slot, uuid, start))
    if selectors != 1:
        raise HTTPException(422, "provide exactly one of: slot, uuid, or start+end")

    if slot is not None:
        where.append(f"sb.slot_number = ${len(args) + 1}")
        args.append(slot)
    elif uuid is not None:
        where.append(f"sb.uuid = ${len(args) + 1}")
        args.append(hex_to_bytes(uuid))
    else:
        where.append(f"sb.submission_ts >= ${len(args) + 1}")
        args.append(start)
        where.append(f"sb.submission_ts < ${len(args) + 1}")
        args.append(end)

    return await run_page(COLUMNS, where, args, "sb.submission_ts DESC", page)
