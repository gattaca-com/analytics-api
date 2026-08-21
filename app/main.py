from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import close_pool, init_pool, ping
from app.ratelimit import RateLimitMiddleware
from app.routers import (
    bid_adjustments,
    blocks,
    delivered_payloads,
    submitted_blocks,
    transaction_sources,
    transactions,
    winning_bids,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(
    title="Gattaca Analytics API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)

app.include_router(blocks.router)
app.include_router(transactions.router)
app.include_router(bid_adjustments.router)
app.include_router(winning_bids.router)
app.include_router(delivered_payloads.router)
# /bid-submissions disabled for now: slot lookups on the hypertable are too
# slow even with a derived time window (see routers/bid_submissions.py)
app.include_router(submitted_blocks.router)
app.include_router(transaction_sources.router)


@app.get("/health", tags=["meta"], summary="Liveness + DB connectivity check")
async def health():
    return {"status": "ok", "db": await ping()}
