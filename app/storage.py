import asyncio

import asyncpg
from asyncpg import Pool


async def get_conn_poll() -> Pool:
    attempt = 0
    while attempt < 5:
        try:
            pool = await asyncpg.create_pool(
                dsn="postgres://postgres:postgres@postgres:5432/postgres"
            )
            return pool
        except OSError:
            await asyncio.sleep(2)
            attempt += 1
    raise OSError


async def ping(pool):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT 1')
