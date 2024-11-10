from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.params import Query
from starlette import status

import models.models
from classes.classes import BaseRecipe, BaseIngredient, BaseRecipeCreate
from sqlalchemy.orm import Session, joinedload
from typing import Annotated, List

from utils.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# annotation for dependency injection
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/ingredient/all")
async def getAllIngredient(db: db_dependency):
    return db.query(models.models.Ingredient).all()


@router.put("/ingredient/edit")
async def updateIngredient(db: db_dependency):
    return db.query(models.models.Recipe).all()


@router.post("/ingredient/add")
async def createIngredient(db: db_dependency, ingredient: BaseIngredient):
    db_ingredient = models.models.Ingredient(**ingredient.dict())
    db_ingredient.created_by = 1
    db_ingredient.currentQuantity = 0
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient
