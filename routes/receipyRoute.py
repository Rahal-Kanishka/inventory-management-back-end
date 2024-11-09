import base64

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


@router.get("/recipe/all")
async def get_all_recipes(db: db_dependency):
    return db.query(models.models.Recipe).all()


@router.put("/recipe/edit")
async def updateRecipe(db: db_dependency):
    return db.query(models.models.Recipe).all()


@router.post("/recipe/add")
async def create_recipe_(db: db_dependency, recipe_data: BaseRecipeCreate):
    ingredient_list = []
    if recipe_data:
        db_recipe = models.models.Recipe(**recipe_data.dict())
        db_recipe.created_by = 1
        ingredient_list.append(db_recipe)
        db.add_all(ingredient_list)
        db.commit()
        db.refresh(db_recipe)
        return db_recipe
