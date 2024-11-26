from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.params import Query
from sqlalchemy import Integer
from sqlalchemy.sql.functions import coalesce
from starlette import status

import models.models
from classes.classes import BaseRecipe, BaseIngredient, BaseRecipeCreate, UpdateBaseIngredient
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func, cast
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
    result = (db
              .query(models.models.Ingredient.id,
                     models.models.Ingredient.name,
                     models.models.Ingredient.description,
                     cast(func.sum(coalesce(models.models.GRN_has_Ingredient.currentQuantity, 0)), Integer).label(
                         'totalQuantity'))
              .join(models.models.GRN_has_Ingredient,
                    models.models.Ingredient.id == models.models.GRN_has_Ingredient.Ingredient_id,
                    isouter=True)
              .group_by(models.models.Ingredient.id, models.models.Ingredient.name,
                        models.models.Ingredient.description)
              .all())
    # convert to dictionary type
    processed_results = [
        {"id": ingredient_id, "name": name, "description": description, "totalQuantity": int(totalQuantity)}
        for ingredient_id, name, description, totalQuantity in result
    ]
    return processed_results


@router.put("/ingredient/edit")
async def updateIngredient(db: db_dependency, updateBaseIngredient: UpdateBaseIngredient):
    db_item = db.query(models.models.Ingredient).filter(models.models.Ingredient.id == updateBaseIngredient.id).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Update the item fields
    db_item.id = updateBaseIngredient.id
    db_item.name = updateBaseIngredient.name
    db_item.description = updateBaseIngredient.description

    # Commit the changes to the database
    db.commit()
    db.refresh(db_item)  # Optional: refresh instance with database values
    print('record updated: ', db_item)

    result = (db
              .query(models.models.Ingredient.id,
                     models.models.Ingredient.name,
                     models.models.Ingredient.description,
                     cast(func.sum(models.models.GRN_has_Ingredient.currentQuantity), Integer).label('totalQuantity'))
              .join(models.models.GRN_has_Ingredient,
                    models.models.Ingredient.id == models.models.GRN_has_Ingredient.Ingredient_id)
              .group_by(models.models.Ingredient.id, models.models.Ingredient.name,
                        models.models.Ingredient.description)
              .filter(models.models.Ingredient.id == db_item.id)
              .first())

    # convert to dictionary type
    if result:
        result_dict = {
            "id": result[0],
            "name": result[1],
            "description": result[2],
            "totalQuantity": result[3],
        }
        print(result_dict)
        return result_dict


@router.post("/ingredient/add")
async def createIngredient(db: db_dependency, ingredient: BaseIngredient):
    db_ingredient = models.models.Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    print('item created: ', db_ingredient.id)
    result = (db
              .query(models.models.Ingredient.id,
                     models.models.Ingredient.name,
                     models.models.Ingredient.description,
                     cast(func.sum(coalesce(models.models.GRN_has_Ingredient.currentQuantity, 0)), Integer).label(
                         'totalQuantity'))
              .join(models.models.GRN_has_Ingredient,
                    models.models.Ingredient.id == models.models.GRN_has_Ingredient.Ingredient_id,
                    isouter=True)
              .group_by(models.models.Ingredient.id, models.models.Ingredient.name,
                        models.models.Ingredient.description)
              .filter(models.models.Ingredient.id == db_ingredient.id)
              .first())

    # convert to dictionary type
    if result:
        result_dict = {
            "id": result[0],
            "name": result[1],
            "description": result[2],
            "totalQuantity": result[3] if result[3] is not None else 0,
        }
        print(result_dict)
        return result_dict
