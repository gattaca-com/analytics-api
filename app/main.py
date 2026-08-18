from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import close_pool, init_pool, ping
from app.routers import bid_adjustments, blocks, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(
    title="Gattaca Analytics API",
    description=(
        "Read-only API over the ethereum warehouse: mined blocks, mined "
        "transactions, and relay bid adjustments. All value fields are "
        "Wei strings; all hashes/addresses are 0x-hex."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(blocks.router)
app.include_router(transactions.router)
app.include_router(bid_adjustments.router)


@app.get("/health", tags=["meta"], summary="Liveness + DB connectivity check")
async def health():
    return {"status": "ok", "db": await ping()}
