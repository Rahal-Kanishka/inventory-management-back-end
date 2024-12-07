from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List

from models import models
from classes.classes import GRNResponse, BaseGRN, IngredientInfo, GRNUpdate
from utils.database import SessionLocal

import logging

# Configure logging with a StreamHandler to force console output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency annotation
db_dependency = Annotated[Session, Depends(get_db)]


# need create, read, update, delete

# create - needs to update Ingredients with new tuple if not existing or update quantity of existing and GRN_has_ingredient
@router.post("/grn/add", response_model=GRNResponse)
async def create_GRN(grn_data: BaseGRN, db: db_dependency):
    # create new GRN tuple
    new_GRN = models.GRN(issuedDate=datetime.now())
    db.add(new_GRN)
    # iterate through the ingredients
    for ingredient_data in grn_data.ingredients:
        # update Ingredient with ingredient quantity
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data.name).first()
        # if ingredient tuple does not exist, return error
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        else:
            db.add(ingredient)
            db.commit()
            db.refresh(ingredient)

            # update GRN_has_Ingredient
            GRN_ingredient = models.GRN_has_Ingredient(
                GRN_id=new_GRN.id,
                Ingredient_id=ingredient.id,
                currentQuantity=ingredient_data.quantity
            )
            db.add(GRN_ingredient)

            # Optionally: Update the current stock of the ingredient
            current_stock = ingredient.current_stock
            if current_stock:
                current_stock.current_quantity += ingredient_data.quantity
            else:
                # Create a new stock record if it doesn't exist
                new_stock = models.CurrentStock(
                    Ingredient_id=ingredient.id,
                    current_quantity=ingredient_data.quantity
                )
                db.add(new_stock)
            db.commit()
            db.refresh(new_GRN)
    return GRNResponse(
        id=new_GRN.id,
        issuedDate=new_GRN.issuedDate,
        ingredients=grn_data.ingredients
    )


# read - should get all ingredients involved with GRN
@router.get("/grn/view_all", response_model=List[GRNResponse])
async def view_all_grns(db: db_dependency):
    # get all grns
    grns = db.query(models.GRN).all()

    all_grns = []
    for grn in grns:
        # Get the ingredients associated with the grn
        grn_ingredients = db.query(models.GRN_has_Ingredient).filter(
            models.GRN_has_Ingredient.GRN_id == grn.id
        ).all()

        # Get ingredient info associated with the grn
        ingredients = []
        for grn_ingredient in grn_ingredients:
            ingredient = db.query(models.Ingredient).filter(
                models.Ingredient.id == grn_ingredient.Ingredient_id
            ).first()
            if ingredient:
                ingredients.append(
                    IngredientInfo(name=ingredient.name, quantity=grn_ingredient.currentQuantity)
                )

        # Append GRN details to the list
        all_grns.append(
            GRNResponse(
                id=grn.id,
                issuedDate=grn.issuedDate,
                ingredients=ingredients
            )
        )

    return all_grns


# view specific GRN
@router.get("/grn/view/{grn_id}", response_model=GRNResponse)
async def view_grn(grn_id: int, db: db_dependency):
    # get grn
    grn = db.query(models.GRN).filter(models.GRN.id == grn_id).first()
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")

    # get ingredients and quantities for the grn
    ingredients_data = (
        db.query(models.Ingredient.name, models.GRN_has_Ingredient.currentQuantity)
        .join(models.GRN_has_Ingredient, models.GRN_has_Ingredient.Ingredient_id == models.Ingredient.id)
        .join(models.GRN, models.GRN.id == models.GRN_has_Ingredient.GRN_id)
        .filter(models.GRN_has_Ingredient.GRN_id == grn_id)
        .all()
    )

    ingredients = [
        IngredientInfo(name=ingredient_name, quantity=quantity)
        for ingredient_name, quantity in ingredients_data
    ]

    # Step 4: Format and return the response
    return GRNResponse(
        id=grn.id,
        issuedDate=grn.issuedDate,
        ingredients=ingredients
    )


# update - needs to update GRN_has_ingredients and Ingredients
@router.put("/grn/update/{grn_id}", response_model=GRNResponse)
async def update_grn(grn_id: int, grn_data: GRNUpdate, db: db_dependency):

    grn = db.query(models.GRN).filter(models.GRN.id == grn_id).first()
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")

    grn_ingredient_records = db.query(models.GRN_has_Ingredient).filter(
        models.GRN_has_Ingredient.GRN_id == grn_id
    ).all()

    grn_ingredient_map = {record.Ingredient_id: record for record in grn_ingredient_records}

    updated_ingredient_names = {ingredient.name for ingredient in grn_data.ingredients}

    ingredient_map = {}
    for new_ingredient in grn_data.ingredients:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == new_ingredient.name).first()
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient '{new_ingredient.name}' not found")
        ingredient_map[ingredient.id] = new_ingredient

    for grn_ingredient in grn_ingredient_records:
        if grn_ingredient.Ingredient_id not in ingredient_map:
            # Missing ingredient
            stock = db.query(models.CurrentStock).filter(
                models.CurrentStock.Ingredient_id == grn_ingredient.Ingredient_id
            ).first()
            if stock:
                stock.current_quantity -= grn_ingredient.currentQuantity
                db.add(stock)
            db.delete(grn_ingredient)

    for ingredient_id, new_ingredient_data in ingredient_map.items():
        if ingredient_id not in grn_ingredient_map:
            # New ingredient
            stock = db.query(models.CurrentStock).filter(
                models.CurrentStock.Ingredient_id == ingredient_id
            ).first()
            if not stock:
                raise HTTPException(status_code=404, detail=f"Stock record for ingredient ID '{ingredient_id}' not found")
            stock.current_quantity += new_ingredient_data.quantity
            db.add(stock)

            ingredient_id = int(ingredient.id)

            new_grn_ingredient = models.GRN_has_Ingredient(
                GRN_id=grn_id,
                Ingredient_id=ingredient_id,
                currentQuantity=new_ingredient_data.quantity
            )
            db.add(new_grn_ingredient)

    db.commit()

    for ingredient_id, grn_ingredient in grn_ingredient_map.items():
        if ingredient_id in ingredient_map:
            new_quantity = ingredient_map[ingredient_id].quantity
            old_quantity = grn_ingredient.currentQuantity

            if new_quantity != old_quantity:
                difference = new_quantity - old_quantity
                stock = db.query(models.CurrentStock).filter(
                    models.CurrentStock.Ingredient_id == ingredient_id
                ).first()
                if stock:
                    stock.current_quantity += difference
                    db.add(stock)

                grn_ingredient.currentQuantity = new_quantity
                db.add(grn_ingredient)

    db.commit()

    if grn_data.issuedDate:
        grn.issuedDate = grn_data.issuedDate
        db.add(grn)
        db.commit()
    return await view_grn(grn_id, db)


