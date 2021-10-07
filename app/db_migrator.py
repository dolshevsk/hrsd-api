from os import listdir
from os.path import dirname, join
from typing import Union

from asyncpg import Connection, Pool


async def run_migrations(conn: Union[Connection, Pool]):
    dir_path = join(dirname(__file__), "migrations")
    files = sorted([f for f in listdir(dir_path)])

    for file in files:
        with open(join(dir_path, file), "r") as f:
            await conn.execute(f.read())
