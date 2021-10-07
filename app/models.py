from typing import Union
from uuid import UUID

from pydantic import BaseModel, validator, Field
from datetime import datetime


class CreateRestaurantResource(BaseModel):
    name: str
    description: str

    @validator("name")
    def name_to_lower(cls, v: str):
        return v.lower()

    @validator("description")
    def should_be_longer_than_4_characters(cls, v: str):
        if len(v) < 4:
            raise ValueError("should be longer than 4 characters")
        return v


class Restaurant(BaseModel):
    id: Union[str, UUID]
    name: str
    description: str = ""
    is_deleted: bool
    created_at: datetime

    @validator("id")
    def uuid_to_string(cls, v):
        if issubclass(type(v), UUID):
            return f"{v}"

        try:
            return f"{UUID(v)}"
        except ValueError:
            raise ValueError("id should be a valid uuid")

    @validator("created_at")
    def datetime_to_iso(cls, v):
        return v.isoformat()


class Restaurants(BaseModel):
    __root__: list[Restaurant]