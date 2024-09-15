import base64
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.params import Query
from starlette import status

import models.models
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


def get_ingredient_by_name(ingredient_name: str, db: db_dependency):
    result = db.query(models.models.Ingredient).filter(models.models.Ingredient.name == ingredient_name).first()
    return result


@router.post("/data/save_to_db")
async def save_to_db(db: db_dependency):
    recipe_data = []*10
    # print('recipe data: ', recipe_data['name'], recipe_data['steps'])
    # save to db
    db_array = []
    if recipe_data is not None and len(recipe_data) > 0:
        for index, row in recipe_data.iterrows():
            print('name: ', row['name'])
            recipe = models.models.Recipe(
                name=row['name'], description=row['description'], instructions=row['steps'], favourite=0,
                row_index=row['row_index']
            )

            # process ingredients
            ingredients_array = row['ingredients'].split(',')
            for ingredient_name in ingredients_array:
                # db_ingredient = models.models.Ingredient()
                # ingredient = ingredient.strip()
                if ingredient_name is not None:
                    db_ingredient = get_ingredient_by_name(ingredient_name.strip(), db)
                    if db_ingredient is None:
                        db_ingredient = models.models.Ingredient()
                        db_ingredient.name = ingredient_name
                        recipe.ingredients.append(db_ingredient)
            db_array.append(recipe)
    print('Ready to commit')
    db.add_all(db_array)
    db.commit()
    print('recipe details saved to db')
    return 1