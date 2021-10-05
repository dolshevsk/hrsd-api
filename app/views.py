import json

from aiohttp.web import Request, Response


async def index(request: Request) -> Response:
    return Response(body=json.dumps({"data": "Welcome!"}))
