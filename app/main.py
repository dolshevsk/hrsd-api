import logging
import asyncio
import os

from aiohttp import web

from views import routes
from db import build_dsn, get_conn_poll

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def init_db_pool(app):
    dsn = build_dsn(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        db=os.environ["POSTGRES_DB"],
    )
    app["pool"] = await get_conn_poll(dsn)
    logger.info("POOL WAS CREATED")
    yield
    logger.info("TRYING TO CLOSE POOL")
    await asyncio.wait_for(app["pool"].close(), timeout=5)
    logger.info("POOL WAS SUCCESSFULLY CLOSED")


async def init_app():
    app = web.Application()
    app.router.add_routes(routes)
    app.cleanup_ctx.append(init_db_pool)
    return app


if __name__ == '__main__':
    app = asyncio.get_event_loop().run_until_complete(init_app())
    web.run_app(app)
