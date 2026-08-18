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
    size: int | None
    extra_data: str | None
    builder: str | None
    builder_name: str | None
    proposer: str | None
    proposer_name: str | None
    transaction_fees: str | None
    burnt_fees: str | None
    internal_transfer_fees: str | None
    builder_payment: str | None
    proposer_payment: str | None
    blob_count: int | None
    injected_subsidy_fee: str | None


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


class BlockPage(BaseModel):
    data: list[Block]
    pagination: Pagination


class TransactionPage(BaseModel):
    data: list[Transaction]
    pagination: Pagination


class BidAdjustmentPage(BaseModel):
    data: list[BidAdjustment]
    pagination: Pagination
