import asyncio
import logging
from os import listdir
from os.path import dirname, join
from typing import Union

from asyncpg import Connection, Pool

from db import get_conn

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def run_migrations(conn: Union[Connection, Pool]):
    dir_path = join(dirname(__file__), "migrations")
    files = sorted([f for f in listdir(dir_path)])

    for file in files:
        with open(join(dir_path, file), "r") as f:
            await conn.execute(f.read())


async def _main():
    conn = await get_conn("postgres_db")
    logger.info("RUNNING MIGRATIONS")
    await run_migrations(conn)
    await asyncio.wait_for(conn.close(), timeout=5)
    logger.info("MIGRATIONS WERE SET SUCCESSFULLY")

if __name__ == '__main__':
    asyncio.run(_main())
