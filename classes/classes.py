from datetime import datetime
from datetime import date
from typing import List
from typing import Optional

from pydantic import BaseModel


class BaseIngredient(BaseModel):
    name: str
    description: str


class BaseRecipeCreate(BaseModel):
    name: str
    description: str


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

class BaseBatchCreate(BaseModel):
    name: str
    productionDate: date
    Recipe_id: int
    initialQuantity: int
    availableQuantity: int
    dateOfExpiry: date
    User_id: int

class BaseBatch(BaseBatchCreate):
    id: Optional[int] = None
