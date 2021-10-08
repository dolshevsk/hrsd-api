from asyncpg import UniqueViolationError
from pydantic import ValidationError
from aiohttp.web import RouteTableDef, Request, Response

from db import (
    fetch_all_restaurants,
    fetch_restaurant_by_name,
    fetch_random_restaurant,
    delete_restaurant_by_name,
    insert_restaurant,
    set_restaurant,
)
from helpers import ResponseJSON, ResponseERROR, Response404
from mappers import from_restaurant_resource
from models import RestaurantResource

routes = RouteTableDef()


@routes.get("")
async def index(request: Request) -> Response:
    return ResponseJSON(data="Welcome!")


@routes.get("/restaurants")
async def list_restaurants(request: Request) -> Response:
    restaurants = await fetch_all_restaurants(request.app["pool"])
    return ResponseJSON(data=restaurants.dict())


@routes.post("/restaurants")
async def create_restaurant(request: Request) -> Response:
    try:
        data = await request.json()
        restaurant = RestaurantResource(**data)
        restaurant = await insert_restaurant(request.app["pool"], restaurant)
    except ValidationError as err:
        return ResponseERROR(f"{err}", status=400)
    except UniqueViolationError as err:
        return ResponseERROR(f"Unique constraint error: {err.detail}", status=409)
    return ResponseJSON(data=restaurant.dict(), status=201)


@routes.get("/restaurants/{name}")
async def retrieve_restaurant(request: Request) -> Response:
    name = request.match_info["name"]
    restaurant = await fetch_restaurant_by_name(request.app["pool"], name)
    if not restaurant:
        return Response404()
    return ResponseJSON(data=restaurant.dict())


@routes.get("/random-restaurant")
async def random_restaurant(request: Request) -> Response:
    restaurant = await fetch_random_restaurant(request.app["pool"])
    if not restaurant:
        return Response404()
    return ResponseJSON(data=restaurant.dict())


@routes.put("/restaurants/{name}")
async def updated_restaurant(request: Request) -> Response:
    name = request.match_info["name"]
    restaurant = await fetch_restaurant_by_name(request.app["pool"], name)
    if not restaurant:
        return Response404()

    try:
        data = await request.json()
        resource = RestaurantResource(**data)
        restaurant = from_restaurant_resource(resource, restaurant)
        await set_restaurant(request.app["pool"], name, restaurant)
    except ValidationError as err:
        return ResponseERROR(f"{err}", status=400)
    except UniqueViolationError as err:
        return ResponseERROR(f"Unique constraint error: {err.detail}", status=409)
    return ResponseJSON(data=restaurant.dict(), status=200)


@routes.delete("/restaurants/{name}")
async def remove_restaurant(request: Request) -> Response:
    name = request.match_info["name"]
    restaurant = await fetch_restaurant_by_name(request.app["pool"], name)
    if not restaurant:
        return Response404()
    await delete_restaurant_by_name(request.app["pool"], name)
    return Response(status=204)
