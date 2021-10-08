import logging
import os
from os import listdir
from os.path import dirname, join
from typing import Union

import asyncio
from asyncpg import Connection, Pool

from db import get_conn, build_dsn

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def run_migrations(conn: Union[Connection, Pool]):
    dir_path = join(dirname(__file__), "migrations")
    files = sorted([f for f in listdir(dir_path)])

    for file in files:
        with open(join(dir_path, file), "r") as f:
            await conn.execute(f.read())


async def _main():
    dsn = build_dsn(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        db=os.environ["POSTGRES_DB"],
    )
    conn = await get_conn(dsn)
    logger.info("RUNNING MIGRATIONS")
    await run_migrations(conn)
    await asyncio.wait_for(conn.close(), timeout=5)
    logger.info("MIGRATIONS WERE SET SUCCESSFULLY")

if __name__ == '__main__':
    asyncio.run(_main())
