from datetime import datetime

from pydantic import BaseModel

from app.pagination import Pagination


class Block(BaseModel):
    number: int
    timestamp: datetime
    slot_number: int
    hash: str
    gas_used: int | None
    gas_limit: int | None
    base_fee_per_gas: int | None
    extra_data: str | None
    builder: str | None
    proposer: str | None
    proposer_name: str | None
    transaction_fees: str | None
    burnt_fees: str | None
    internal_transfer_fees: str | None
    builder_payment: str | None
    proposer_payment: str | None


class Transaction(BaseModel):
    hash: str
    block_number: int | None
    timestamp: datetime
    index: int | None
    success: bool | None
    to_address: str | None
    from_address: str | None
    type: int | None
    gas_used: int | None
    priority_fee_per_gas: str | None
    priority_fee: str | None
    internal_transfer_fee: str | None
    kickback: str | None
    value: str | None
    merge_contributor: str | None


class BidAdjustment(BaseModel):
    relay_id: int
    relay: str | None
    slot_number: int
    block_number: int
    adjusted_block_hash: str
    adjusted_value: str
    builder_pubkey_id: int
    builder_pubkey: str | None
    builder_extra_data: str | None
    delta: str
    fee: int
    submitted_block_hash: str
    submitted_received_at: datetime
    submitted_value: str | None


class WinningBid(BaseModel):
    slot_number: int
    winning_timestamp: datetime
    winning_relay_id: int
    relay: str | None
    block_hash: str | None
    winning_bid_value: str | None
    other_relay_ids: list[int] | None
    block_uuid: str | None
    is_passthrough: bool | None


class DeliveredPayload(BaseModel):
    relay_id: int
    relay: str | None
    slot_number: int
    block_number: int
    block_hash: str
    builder_pubkey_id: int
    builder_pubkey: str | None
    builder_extra_data: str | None
    proposer_pubkey: str
    proposer_fee_recipient: str
    gas_limit: int
    gas_used: int
    value: str


class BidSubmission(BaseModel):
    relay_id: int
    relay: str | None
    slot_number: int
    block_number: int
    block_hash: str
    builder_pubkey_id: int
    builder_pubkey: str | None
    builder_extra_data: str | None
    value: str
    timestamp: datetime


class SubmittedBlock(BaseModel):
    uuid: str
    builder_id: int | None
    builder: str | None
    strategy_id: int | None
    strategy: str | None
    slot_number: int | None
    builder_payment: str | None
    raw_builder_payment: str | None
    gas_used: int | None
    on_build_start: datetime
    on_build_finish: datetime
    submission_ts: datetime | None
    orders_count: int | None
    bundles_count: int | None
    eob_bundles: int | None
    blobs_count: int | None
    sim_time: int | None
    block_type_id: int | None
    block_type: str | None
    removed_ts: datetime | None
    removed_reason_id: int | None
    removed_reason: str | None
    removed_triggering_block: str | None
    eob_value: str | None
    cex_dex_value: str | None
    best_order_value: str | None


class TransactionSource(BaseModel):
    timestamp: datetime
    hash: str | None
    entry_point_id: int | None
    entry_point: str | None
    source_id: int | None
    source: str | None
    region_id: int | None
    region: str | None
    bundle_hash: str | None


class BlockPage(BaseModel):
    data: list[Block]
    pagination: Pagination


class TransactionPage(BaseModel):
    data: list[Transaction]
    pagination: Pagination


class BidAdjustmentPage(BaseModel):
    data: list[BidAdjustment]
    pagination: Pagination


class WinningBidPage(BaseModel):
    data: list[WinningBid]
    pagination: Pagination


class DeliveredPayloadPage(BaseModel):
    data: list[DeliveredPayload]
    pagination: Pagination


class BidSubmissionPage(BaseModel):
    data: list[BidSubmission]
    pagination: Pagination


class SubmittedBlockPage(BaseModel):
    data: list[SubmittedBlock]
    pagination: Pagination


class TransactionSourcePage(BaseModel):
    data: list[TransactionSource]
    pagination: Pagination
