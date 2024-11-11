from datetime import datetime
from datetime import date
from typing import List
from typing import Optional

from pydantic import BaseModel


class BaseIngredient(BaseModel):
    name: str
    description: Optional[str] = ""

class RecipeIngredientCreate(BaseModel):
    name: str
    quantity: int

class IngredientInfo(BaseModel):
    name: str
    quantity: int

class RecipeViewResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    product_type: Optional[str] = ""
    ingredients: List[IngredientInfo] = []

class BaseRecipeCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    product_name: Optional[str] = "Miscellaneous"
    ingredients: List[RecipeIngredientCreate]


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""

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

class LocationBase(BaseModel):
    name: str
    address: str

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    name: str
    address: str

    class Config:
        from_attributes = True
