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
    new_GRN = models.GRN(issuedDate=grn_data.issuedDate)
    db.add(new_GRN)
    # iterate through the ingredients
    for ingredient_data in grn_data.ingredients:
        # update Ingredient with ingredient quantity
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data.name).first()
        # if ingredient tuple does not exist, return error
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        else:
            # if ingredient tuple already exists increase its quantity
            ingredient.currentQuantity += ingredient_data.quantity
            db.add(ingredient)
            db.commit()
            db.refresh(ingredient)

            # update GRN_has_Ingredient
            GRN_ingredient = models.GRN_has_Ingredient(
                GRN_id=new_GRN.id,
                Ingredient_id=ingredient.id,
                quantity=ingredient_data.quantity
            )
            db.add(GRN_ingredient)
            db.commit()

            db.refresh(new_GRN)
        
    return GRNResponse (
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
                    IngredientInfo(name=ingredient.name, quantity=grn_ingredient.quantity)
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
        db.query(models.Ingredient.name, models.GRN_has_Ingredient.quantity)
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
@router.patch("/grn/update/{grn_id}", response_model=GRNResponse)
async def update_grn(grn_id: int, grn_data: GRNUpdate, db: db_dependency):
    # Fetch the GRN to ensure the grn exists
    grn = db.query(models.GRN).filter(models.GRN.id == grn_id).first()
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")
    
    # Update recipe name and description if provided
    if grn_data.issuedDate:
        grn.issuedDate = grn_data.issuedDate
    
    # Update ingredients if ingredients are different in update
    if grn_data.ingredients:
        # loop through each updated ingredient
        for ingredient_data in grn_data.ingredients:
            # find ingredient in Ingredient table
            ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data.name).first()
            # check whether ingredient is in table
            if ingredient:
                # if ingredient is found
                # find old quantity to update ingredient table with
                old = db.query(models.GRN_has_Ingredient.quantity).join(
                models.GRN, models.GRN_has_Ingredient.GRN_id == models.GRN.id
                ).filter(
                models.GRN_has_Ingredient.GRN_id == grn.id,
                models.GRN_has_Ingredient.Ingredient_id == ingredient.id
                ).first()

                if old:
                    old_quantity = old[0]
                else: 
                    old_quantity = 0
                
                # update ingredient
                if old_quantity != ingredient_data.quantity:
                    ingredient.currentQuantity = (ingredient.currentQuantity - old_quantity + ingredient_data.quantity)
                    db.add(ingredient)
                    db.commit()
                    db.refresh(ingredient)
                
                # update grn has ingredient table
                grn_has_ingredient = db.query(models.GRN_has_Ingredient).filter(models.GRN_has_Ingredient.GRN_id == grn_id).first()
                grn_has_ingredient.Ingredient_id = ingredient.id
                grn_has_ingredient.quantity = ingredient_data.quantity
                db.add(grn_has_ingredient)
                db.commit()
                db.refresh(grn_has_ingredient)
            else:
                # if ingredient is not found
                raise HTTPException(status_code=404, detail="Ingredient not found")

    # Commit all changes
    db.commit()

    # Fetch updated recipe with related data
    return await view_grn(grn_id, db)

# delete - needs to update GRN_has_ingredients and Ingredients