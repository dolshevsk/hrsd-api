import json

from pydantic import ValidationError
from aiohttp.web import RouteTableDef, Request, Response

from models import CreateRestaurantResource
from helpers import ResponseJSON, ResponseERROR
from db import fetch_all_restaurants, fetch_restaurant_by_name, insert_restaurant

routes = RouteTableDef()


@routes.get("")
async def index(request: Request) -> Response:
    return Response(body=json.dumps({"data": "Welcome!"}))


@routes.post("/restaurants")
async def create_restaurant(request: Request) -> Response:
    data = await request.json()
    try:
        restaurant = CreateRestaurantResource(**data)
    except ValidationError as err:
        return ResponseERROR(message=f"{err}", status=400)
    restaurant = await insert_restaurant(request.app["pool"], restaurant)
    return ResponseJSON(data=restaurant.dict(), status=201)


@routes.get("/restaurants")
async def list_restaurant(request: Request) -> Response:
    restaurants = await fetch_all_restaurants(request.app["pool"])
    return ResponseJSON(data=restaurants.dict()["__root__"])


@routes.get("/restaurants/{name}")
async def retrieve_restaurant(request: Request) -> Response:
    name = request.match_info["name"]
    restaurant = await fetch_restaurant_by_name(request.app["pool"], name)
    return ResponseJSON(data=restaurant.dict())
