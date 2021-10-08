from datetime import datetime
import pytest

from aiohttp import web

from models import RestaurantResource
from db import get_conn, get_conn_poll, insert_restaurant
from db_migrator import run_migrations
from views import routes


@pytest.fixture()
async def test_db_pool():
    # get default db conn
    conn = await get_conn("postgres")
    # create test_db
    await conn.execute(f"DROP DATABASE IF EXISTS test_db")
    await conn.execute("CREATE DATABASE test_db")
    # get test_db pool of connections
    pool = await get_conn_poll("test_db")
    # run migrations
    await run_migrations(pool)
    yield pool
    # close pool of connections
    await pool.close()
    # drop test_db and close conn
    await conn.execute("DROP DATABASE test_db WITH (FORCE)")
    await conn.close()


@pytest.fixture
def app(test_db_pool):
    app = web.Application()
    app.router.add_routes(routes)
    app["pool"] = test_db_pool
    return app


@pytest.fixture
def client(app, aiohttp_client, loop):
    return loop.run_until_complete(aiohttp_client(app))


async def test_index(client):
    resp = await client.get('/')
    assert resp.status == 200
    json = await resp.json()
    assert json["data"] == "Welcome!"


async def test_list_restaurants_against_empty_db(client):
    resp = await client.get("/restaurants")
    assert resp.status == 200
    json = await resp.json()
    assert json["data"] == []


async def test_list_restaurants_ordered(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="A", description="shorty"))
    await insert_restaurant(app["pool"], RestaurantResource(name="B", description="shorty"))

    resp = await client.get("/restaurants")
    assert resp.status == 200
    json = await resp.json()
    data = json["data"]
    assert len(data) == 2
    assert datetime.fromisoformat(data[0]["created_at"]) > datetime.fromisoformat(data[1]["created_at"])


async def test_create_restaurant_400_on_empty_name(client, app):
    resp = await client.post("/restaurants", json={"name": "", "description": "short"})
    assert resp.status == 400


async def test_create_restaurant_400_on_empty_description(client, app):
    resp = await client.post("/restaurants", json={"name": "Vasilki", "description": ""})
    assert resp.status == 400


async def test_create_restaurant_400_on_short_description(client, app):
    resp = await client.post("/restaurants", json={"name": "Vasilki", "description": "bad"})
    assert resp.status == 400


async def test_create_restaurant_409_when_unique_constraint(client, app):
    resp = await client.post("/restaurants", json={"name": "Vasilki", "description": "random1"})
    assert resp.status == 201

    resp = await client.post("/restaurants", json={"name": "Vasilki", "description": "random2"})
    assert resp.status == 409
    json = await resp.json()
    assert "Unique" in json["message"]


async def test_create_restaurant_201_on_success_and_lower_name(client, app):
    resp = await client.post("/restaurants", json={"name": "Vasilki", "description": "random1"})
    assert resp.status == 201
    json = await resp.json()
    assert json["data"]["name"] == "vasilki"


async def test_retrieve_restaurant_404_not_found(client, app):
    resp = await client.get("/restaurants/vasilki")
    assert resp.status == 404


async def test_retrieve_restaurant_200_case_intensive(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="Doma", description="shorty"))

    resp = await client.get("/restaurants/DOMA")
    assert resp.status == 200
    json = await resp.json()
    assert bool(json["data"]["id"]) is True


async def test_retrieve_restaurant_200_on_success(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="Vasilki", description="shorty"))

    resp = await client.get("/restaurants/vasilki")
    assert resp.status == 200
    json = await resp.json()
    assert bool(json["data"]["id"]) is True


async def test_random_restaurant_404_against_empty_db(client, app):
    resp = await client.get("/random_restaurants")
    assert resp.status == 404


async def test_random_restaurant_200(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="A", description="shorty"))
    await insert_restaurant(app["pool"], RestaurantResource(name="B", description="shorty"))

    resp = await client.get("/random-restaurant")
    assert resp.status == 200
    json = await resp.json()
    assert type(json["data"]) == dict


async def test_update_restaurant_404_not_found(client, app):
    resp = await client.put("/restaurants/myka")
    assert resp.status == 404


async def test_update_restaurant_400_validation_works(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="BackDoor", description="hamburgers"))

    resp = await client.put("/restaurants/backdoor", json={"name": ""})
    assert resp.status == 400


async def test_update_restaurant_409_unique_constraint(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="BlackHole", description="hamburgers"))
    await insert_restaurant(app["pool"], RestaurantResource(name="Enzo", description="hamburgers"))

    resp = await client.put("/restaurants/blackhole", json={"name": "enzo", "description": "random"})
    assert resp.status == 409


async def test_update_restaurant_200_can_update(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="Depo", description="sandwiches"))

    resp = await client.put("/restaurants/depo", json={"name": "miesto", "description": "poland dishes"})
    assert resp.status == 200
    json = await resp.json()
    assert json["data"]["name"] == "miesto"
    assert json["data"]["description"] == "poland dishes"


async def test_remove_restaurant_404_not_found(client, app):
    resp = await client.delete("/restaurants/pizza-tempo")
    assert resp.status == 404


async def test_remove_restaurant_200_on_success(client, app):
    await insert_restaurant(app["pool"], RestaurantResource(name="SeaFoodBar", description="shorty"))

    resp = await client.delete("/restaurants/seafoodbar")
    assert resp.status == 204
