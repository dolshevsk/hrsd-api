import views

from aiohttp.web import Application


def setup_routes(app: Application):
    app.router.add_get("/", views.index)
