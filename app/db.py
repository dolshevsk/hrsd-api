from typing import Optional

import asyncpg
from asyncpg import Pool, Connection

from models import RestaurantResource, Restaurant, Restaurants
from utils import io_attempts


@io_attempts(5)
async def get_conn(db_name: str) -> Connection:
    conn = await asyncpg.connect(
        dsn=f"postgres://postgres:postgres@127.0.0.1:5432/{db_name}"
    )
    return conn


@io_attempts(5)
async def get_conn_poll(db_name: str) -> Pool:
    pool = await asyncpg.create_pool(
        dsn=f"postgres://postgres:postgres@127.0.0.1:5432/{db_name}"
    )
    return pool


async def insert_restaurant(pool: Pool, restaurant: RestaurantResource) -> Restaurant:
    row = await pool.fetchrow(
        "INSERT INTO restaurants (name, description) VALUES ($1, $2) RETURNING id, created_at",
        restaurant.name,
        restaurant.description,
    )
    restaurant = Restaurant(**row, **restaurant.dict())
    return restaurant


async def set_restaurant(pool: Pool, old_name: str, restaurant: Restaurant) -> bool:
    result = await pool.execute(
        "UPDATE restaurants SET name=$1, description=$2 WHERE name ILIKE $3",
        restaurant.name,
        restaurant.description,
        old_name,
    )
    return bool(int(result.removeprefix("UPDATE ")))


async def fetch_all_restaurants(pool: Pool) -> Restaurants:
    rows = await pool.fetch("SELECT * FROM restaurants ORDER BY created_at DESC")
    restaurants = Restaurants.parse_obj(rows)
    return restaurants


async def fetch_restaurant_by_name(pool: Pool, name: str) -> Optional[Restaurant]:
    row = await pool.fetchrow("SELECT * FROM restaurants where name ILIKE $1", name)
    if not row:
        return None

    restaurant = Restaurant(**row)
    return restaurant


async def delete_restaurant_by_name(pool: Pool, name: str) -> bool:
    result = await pool.execute("DELETE FROM restaurants where name ILIKE $1", name)  # response -> "DELETE 1"
    return bool(int(result.removeprefix("DELETE ")))
