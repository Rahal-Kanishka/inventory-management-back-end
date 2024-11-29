from datetime import datetime
from datetime import date
from typing import List
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel


class BaseIngredient(BaseModel):
    name: str
    description: Optional[str] = ""


class UpdateBaseIngredient(BaseModel):
    id: int
    name: str
    description: str

class RecipeIngredientCreate(BaseModel):
    name: str
    quantity: int

class IngredientInfo(BaseModel):
    name: str
    quantity: int

# create GRN
class BaseGRN(BaseModel):
    ingredients: List[IngredientInfo] = []

# response for create GRN
class GRNResponse(BaseModel):
    id: int
    issuedDate: datetime
    ingredients: List[IngredientInfo] = []


# update GRN
class GRNUpdate(BaseModel):
    issuedDate: Optional[date] = None
    ingredients: Optional[List[IngredientInfo]] = None


class RecipeViewResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    ingredients: List[IngredientInfo] = []

class BaseRecipeCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    product_name: Optional[str] = "Miscellaneous"
    ingredients: List[RecipeIngredientCreate]

class RecipeIngredientUpdate(BaseModel):
    name: str
    quantity: int

class BaseRecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_name: Optional[str] = None
    ingredients: Optional[List[RecipeIngredientUpdate]] = None


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
    name: str
    email: str
    contactNo: str
    password: str
    UserType_id: int
    createdOn: datetime = datetime.now()


class UpdateBaseUser(BaseModel):
    id: int
    name: str
    email: str
    contactNo: str
    password: str
    UserType_id: int

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


class SearchUsersForLocation(BaseModel):
    name: str
    locationID: int


class CreateProduct(BaseModel):
    name: str
    description: str
    type: str
    selling_price: Decimal = 0.0
    Recipe_id: int


class UpdateProduct(BaseModel):
    id: int
    name: str
    description: str
    type: str
    selling_price: Decimal = 0.0
    Recipe_id: int