import asyncpg

from app.config import settings

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            min_size=settings.db_pool_min,
            max_size=settings.db_pool_max,
            command_timeout=settings.statement_timeout_seconds,
        )


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def fetch(query: str, *args) -> list[asyncpg.Record]:
    assert _pool is not None, "pool not initialized"
    async with _pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def ping() -> bool:
    assert _pool is not None, "pool not initialized"
    async with _pool.acquire() as conn:
        return (await conn.fetchval("SELECT 1")) == 1
