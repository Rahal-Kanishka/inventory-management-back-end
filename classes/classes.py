from datetime import datetime
from typing import List

from pydantic import BaseModel


class BaseIngredient(BaseModel):
    id: int
    name: str
    description: str
    image: str


class BaseRecipeCreate(BaseModel):
    name: str
    id: int
    description: str
    instructions: str


class BaseRecipe(BaseModel):
    name: str
    id: int
    description: str
    instructions: str
    ingredients: List[BaseIngredient] = []


class BaseUser(BaseModel):
    id: int
    name: str
    username: str
    password: str
    email: str
    type: int
    created_on: datetime = datetime.now()
