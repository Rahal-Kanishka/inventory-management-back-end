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
    # update GRN with tuples
    for ingredient_data in grn_data.ingredients:
        # create new GRN tuple for each ingredient
        new_GRN = models.GRN(issuedDate=grn_data.issuedDate, quantity=ingredient_data.quantity)
        db.add(new_GRN)
        db.commit()

        # update Ingredient with ingredient quantity
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data.name).first()
        # if ingredient tuple does not exist, create it
        if not ingredient:
            ingredient = models.Ingredient(name=ingredient_data.name, currentQuantity=ingredient_data.quantity, description="")
            db.add(ingredient)
            db.commit()
            db.refresh(ingredient)
        else:
            # if ingredient tuple already exists increase its quantity
            ingredient.currentQuantity += ingredient_data.quantity
            db.add(ingredient)
            db.commit()
            db.refresh(ingredient)

        # update GRN_has_Ingredient
        GRN_ingredient = models.GRN_has_Ingredient(
            GRN_id=new_GRN.id,
            Ingredient_id=ingredient.id
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
                    IngredientInfo(name=ingredient.name, quantity=grn.quantity)
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
        db.query(models.Ingredient.name, models.GRN.quantity)
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
    # Fetch the GRN
    grn = db.query(models.GRN).filter(models.GRN.id == grn_id).first()
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")
    
    # Update recipe name and description if provided
    if grn_data.issuedDate:
        grn.issuedDate = grn_data.issuedDate

    # Update ingredients
    if grn_data.ingredients:
        existing_ingredients = {(gi.Ingredient_id, gi.GRN_id) for gi in db.query(models.GRN_has_Ingredient).filter(
            models.GRN_has_Ingredient.GRN_id == grn.id)}

        for ingredient_data in grn_data.ingredients:
            # Check if ingredient already exists
            ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data.name).first()
            # if ingredient is not found
            if not ingredient:
                ingredient = models.Ingredient(name=ingredient_data.name, currentQuantity=ingredient_data.quantity, description="")
                db.add(ingredient)
                db.commit()
                db.refresh(ingredient)

            # If ingredient is a newly added one, add relation to grn
            if (ingredient.id, grn.id) not in existing_ingredients:
                grn_ingredient = models.GRN_has_Ingredient(
                    GRN_id=grn.id,
                    Ingredient_id=ingredient.id
                )
                db.add(grn_ingredient)
                # if ingredient already exists...
            else:
                # Update quantity if different which is done by taking current quantity from Ingredients table
                # subtracting the old quantity from GRN table, and adding the new quantity fomr ingredient_data.quantity
                old = db.query(models.GRN.quantity).join(
                models.GRN_has_Ingredient, models.GRN.id == models.GRN_has_Ingredient.GRN_id
                ).filter(
                models.GRN_has_Ingredient.GRN_id == grn.id,
                models.GRN_has_Ingredient.Ingredient_id == ingredient.id
                ).first()
                
                if old[0] != ingredient_data.quantity:
                    grn.quantity = ingredient_data.quantity
                    ingredient.currentQuantity = (ingredient.currentQuantity - old[0] + ingredient_data.quantity)
                    db.add(ingredient)
                    db.commit()
                    db.refresh(ingredient)

            # Remove the ingredient from the tracking dictionary if it's still part of the grn
            existing_ingredients.discard((ingredient.id, grn.id))

        # Remove any ingredients that are no longer needed
        for ingredient_id, grn_id in existing_ingredients:
            db.query(models.GRN_has_Ingredient).filter(
                models.GRN_has_Ingredient.GRN_id == grn.id,
                models.GRN_has_Ingredient.Ingredient_id == ingredient_id
            ).delete()

    # Commit all changes
    db.commit()

    # Fetch updated recipe with related data
    return await view_grn(grn_id, db)


# delete - needs to update GRN_has_ingredients and Ingredients