import asyncio

from aiohttp import web

from routes import setup_routes
from storage import get_conn_poll, ping


async def init_app():
    pool = await get_conn_poll()
    await ping(pool)

    app = web.Application()
    setup_routes(app)
    return app


if __name__ == '__main__':
    app = asyncio.get_event_loop().run_until_complete(init_app())
    web.run_app(app)
