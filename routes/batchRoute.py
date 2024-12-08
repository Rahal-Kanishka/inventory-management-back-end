from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func, cast, Integer
from sqlalchemy.orm import Session, joinedload
from typing import Annotated, List
from datetime import datetime
from dateutil.relativedelta import relativedelta

from models import models
from classes.classes import BaseBatchCreate, BaseBatch  # We'll define BaseBatchCreate for the POST request
from utils.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Annotation for dependency injection
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/batch/all")
async def get_all_batches(db: db_dependency):
    return db.query(models.Batch).options(joinedload(models.Batch.product)).all()


@router.post("/batch/add")
async def create_batch(db: db_dependency, batch_data: BaseBatchCreate):
    new_batch = None
    # validate against product
    batch_product: models.Product = db.query(models.Product).filter(models.Product.id == batch_data.product_id).first()
    if not batch_product:
        raise HTTPException(status_code=404, detail="Product not found")
    # check weather the brewery has enough ingredients to make this batch
    # fetch the ingredients for the recipe in the product
    batch_recipe: models.Recipe = batch_product.recipe
    if not batch_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredients = batch_product.recipe.ingredients
    if not ingredients:
        raise HTTPException(status_code=404, detail="Ingredients not found")

    # get ingredients for the recipe with is quantities
    batch_recipe_ingredients = (db
                                .query(models.RecipeHasIngredient)
                                .filter(models.RecipeHasIngredient.Recipe_id == batch_recipe.id)
                                .all())

    processed_batch_recipe_ingredients = [
        {"ingredient_id": item.Ingredient_id, "Recipe_id": item.Recipe_id, "quantity": int(item.quantity)}
        for item in batch_recipe_ingredients
    ]

    result = db.query(models.CurrentStock).all()
    # convert to dictionary type
    processed_total_ingredients = [
        {"id": item.Ingredient_id, "totalQuantity": int(item.current_quantity)}
        for item in result
    ]

    for ingredient in ingredients:
        # get the current quantity
        total_ingredient_record = next(filter(lambda x: x["id"] == ingredient.id, processed_total_ingredients), None)
        recipe_ingredient_record = next(filter(lambda x: x["ingredient_id"] == ingredient.id,
                                               processed_batch_recipe_ingredients), None)
        # check if current quantity is enough to make batch
        if total_ingredient_record and recipe_ingredient_record:
            if total_ingredient_record["totalQuantity"] < (int(recipe_ingredient_record["quantity"]) * batch_data.batch_count):
                raise HTTPException(status_code=404,
                                    detail="Ingredients not sufficient to make the batch, name: " + ingredient.name)
        else:
            raise HTTPException(status_code=404,
                                detail="Ingredients not sufficient to make the batch, name: " + ingredient.name)

    # creating a batch record and then reduce stocks for ingredients
    expire_data = (datetime.now() + relativedelta(months=batch_product.expire_duration))
    new_batch = models.Batch(
        name='Batch of Product: ' + batch_product.name + ' of type: ' + batch_product.type,
        productionDate=datetime.now(),
        initialQuantity=batch_product.batch_size,
        availableQuantity=batch_product.batch_size,
        dateOfExpiry=expire_data,
        product_id=batch_product.id
    )

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    # reduce the current quantities
    for ingredient in ingredients:
        # get the current quantity
        recipe_ingredient_record = next(filter(lambda x: x["ingredient_id"] == ingredient.id,
                                               processed_batch_recipe_ingredients), None)
        if recipe_ingredient_record:
            current_stock = ingredient.current_stock
            if current_stock:
                current_stock.current_quantity -= (int(recipe_ingredient_record["quantity"]) * batch_data.batch_count)
        db.commit()
    return (db.query(models.Batch)
            .options(joinedload(models.Batch.product))
            .filter(models.Batch.id == new_batch.id)
            .first())
