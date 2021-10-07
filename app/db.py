import asyncio

import asyncpg
from asyncpg import Pool

from models import CreateRestaurantResource, Restaurant, Restaurants


async def get_conn_poll() -> Pool:
    attempt = 0
    while attempt < 5:
        try:
            pool = await asyncpg.create_pool(
                dsn="postgres://postgres:postgres@127.0.0.1:5432/postgres"
            )
            return pool
        except OSError:
            await asyncio.sleep(2)
            attempt += 1
    raise OSError


async def insert_restaurant(pool: Pool, restaurant: CreateRestaurantResource) -> Restaurant:
    row = await pool.fetchrow(
        "INSERT INTO restaurants (name, description, is_deleted) VALUES ($1, $2, false) RETURNING id, is_deleted, created_at",
        restaurant.name,
        restaurant.description,
    )
    restaurant = Restaurant(**row, **restaurant.dict())
    print(f"restaurant={restaurant}")
    return restaurant


async def fetch_all_restaurants(pool: Pool) -> Restaurants:
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM restaurants ORDER BY created_at DESC")

    restaurants = Restaurants.parse_obj(rows)
    # for row in rows:
    #     restaurants.append(Restaurant(**row))

    return restaurants


async def fetch_restaurant_by_name(pool: Pool, name: str) -> Restaurant:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM restaurants where name = $1", name)
    restaurant = Restaurant(**row)
    return restaurant


async def delete_restaurant_by_name(pool: Pool, name: str) -> bool:
    async with pool.acquire() as conn:
        result = await conn.execute("UPDATE restaurants SET is_deleted = true where name = $1", name)
        print(result)

    return True
