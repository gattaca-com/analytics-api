from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import DeliveredPayloadPage
from app.pagination import PageParams
from app.query import hex_to_bytes, run_page

router = APIRouter(prefix="/delivered-payloads", tags=["delivered-payloads"])

COLUMNS = (
    "dp.relay_id, r.relay AS relay, dp.slot_number, dp.block_number, "
    "dp.block_hash, dp.builder_pubkey_id, bp.pubkey AS builder_pubkey, "
    "bp.extra_data AS builder_extra_data, dp.proposer_pubkey, "
    "dp.proposer_fee_recipient, dp.gas_limit, dp.gas_used, dp.value "
    "FROM relay.delivered_payload dp "
    "LEFT JOIN label.relay r ON r.id = dp.relay_id "
    "LEFT JOIN label.builder_pubkey bp ON bp.id = dp.builder_pubkey_id"
)


@router.get(
    "", response_model=DeliveredPayloadPage, summary="List / look up delivered payloads"
)
async def list_delivered_payloads(
    slot: int | None = Query(None, description="Exact slot_number."),
    block: int | None = Query(None, description="Exact block number."),
    hash: str | None = Query(None, description="Block hash (0x-hex)."),
    page: PageParams = Depends(),
):
    """Provide exactly one of `slot`, `block`, or `hash`.

    No timestamp column exists on this table, so range queries are not
    supported.
    """
    where: list[str] = []
    args: list = []
    selectors = sum(x is not None for x in (slot, block, hash))
    if selectors != 1:
        raise HTTPException(422, "provide exactly one of: slot, block, or hash")

    if slot is not None:
        where.append(f"dp.slot_number = ${len(args) + 1}")
        args.append(slot)
    elif block is not None:
        where.append(f"dp.block_number = ${len(args) + 1}")
        args.append(block)
    else:
        where.append(f"dp.block_hash = ${len(args) + 1}")
        args.append(hex_to_bytes(hash))

    return await run_page(COLUMNS, where, args, "dp.slot_number DESC", page)
