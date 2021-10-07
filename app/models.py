from typing import Union
from uuid import UUID

from pydantic import BaseModel, validator, Field, parse_obj_as
from datetime import datetime


class RestaurantResource(BaseModel):
    name: str
    description: str

    @validator("name")
    def name_should_be_at_least_1_character(cls, v: str):
        if len(v) < 1:
            raise ValueError("should be at least 1 character")
        return v

    @validator("name")
    def name_to_lower(cls, v: str):
        return v.lower()

    @validator("description")
    def description_should_be_longer_than_4_characters(cls, v: str):
        if len(v) < 4:
            raise ValueError("should be longer than 4 characters")
        return v


class Restaurant(BaseModel):
    id: Union[str, UUID]
    name: str
    description: str = ""
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

    def dict(self, *args, **kwargs):
        res = super().dict(*args, **kwargs)
        return res["__root__"]
