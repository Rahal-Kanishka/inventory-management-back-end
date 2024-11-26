from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List

from models import models
from classes.classes import BaseRecipeCreate, RecipeResponse, RecipeViewResponse, IngredientInfo, BaseRecipeUpdate, RecipeIngredientUpdate;
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


@router.post("/recipe/add", response_model=RecipeResponse)
async def create_recipe(recipe_data: BaseRecipeCreate, db: db_dependency):
    #logger.info(f"Creating Recipe: {recipe_data.name}")

    # Step 1: Create the Recipe entry
    new_recipe = models.Recipe(name=recipe_data.name, description=recipe_data.description)
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    # Step 2: Process Ingredients
    for ingredient_data in recipe_data.ingredients:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data.name).first()
        if not ingredient:
            ingredient = models.Ingredient(name=ingredient_data.name, currentQuantity=0, description="")
            db.add(ingredient)
            db.commit()
            db.refresh(ingredient)

        recipe_ingredient = models.RecipeHasIngredient(
            Recipe_id=new_recipe.id,
            Ingredient_id=ingredient.id,
            quantity=ingredient_data.quantity
        )
        db.add(recipe_ingredient)
    db.commit()

    # Step 3: Process ProductType
    product_name = recipe_data.product_name
    logger.info(f"Product name provided: {product_name}")

    # Check if ProductType exists with the given product_name
    product_type = db.query(models.ProductType).filter(models.ProductType.name == product_name).first()
    if not product_type:
        logger.info(f"ProductType '{product_name}' not found. Creating new ProductType entry.")
        product_type = models.ProductType(name=product_name, code=product_name[:4].upper(), batchSize=0,
                                          expireDuration=0)
        db.add(product_type)
        db.commit()
        db.refresh(product_type)

    # Check if Product exists with the given product_name
    product = db.query(models.Product).filter(models.Product.name == product_name).first()
    if not product:
        logger.info(f"Product '{product_name}' not found in Product table. Creating new Product entry.")
        product = models.Product(name=product_name, currentQuantity=0, description="default product",
                                 ProductType_id=product_type.id)
        db.add(product)
        db.commit()
        db.refresh(product)

    # Step 4: Link Recipe with ProductType in recipe_has_producttype
    recipe_producttype_link = models.Recipe_has_producttype(Recipe_id=new_recipe.id, ProductType_id=product_type.id)
    db.add(recipe_producttype_link)
    db.commit()

    return RecipeResponse(
        id=new_recipe.id,
        name=new_recipe.name,
        description=new_recipe.description,
        ingredients=recipe_data.ingredients
    )


@router.get("/recipe/view/{recipe_id}", response_model=RecipeViewResponse)
async def view_recipe(recipe_id: int, db: db_dependency):
    # Step 1: Get the Recipe
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Step 2: Get the associated ProductType for the recipe
    product_type = (
        db.query(models.ProductType.name)
        .join(models.Recipe_has_producttype, models.ProductType.id == models.Recipe_has_producttype.ProductType_id)
        .filter(models.Recipe_has_producttype.Recipe_id == recipe_id)
        .first()
    )
    product_type_name = product_type.name if product_type else "N/A"

    # Step 3: Get ingredients and quantities for the recipe
    ingredients_data = (
        db.query(models.Ingredient.name, models.RecipeHasIngredient.quantity)
        .join(models.RecipeHasIngredient, models.Ingredient.id == models.RecipeHasIngredient.Ingredient_id)
        .filter(models.RecipeHasIngredient.Recipe_id == recipe_id)
        .all()
    )

    ingredients = [
        IngredientInfo(name=ingredient_name, quantity=quantity)
        for ingredient_name, quantity in ingredients_data
    ]

    # Step 4: Format and return the response
    return RecipeViewResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        product_type=product_type_name,
        ingredients=ingredients
    )


@router.get("/recipe/view_all", response_model=List[RecipeViewResponse])
async def view_all_recipes(db: db_dependency):
    # Query all recipes
    recipes = db.query(models.Recipe).all()

    all_recipes = []
    for recipe in recipes:
        # Get the product type associated with the recipe
        product_type_link = db.query(models.Recipe_has_producttype).filter(
            models.Recipe_has_producttype.Recipe_id == recipe.id
        ).first()

        product_type_name = "Unknown"
        if product_type_link:
            product_type = db.query(models.ProductType).filter(
                models.ProductType.id == product_type_link.ProductType_id
            ).first()
            if product_type:
                product_type_name = product_type.name

        # Gather all ingredients for the recipe
        recipe_ingredients = db.query(models.RecipeHasIngredient).filter(
            models.RecipeHasIngredient.Recipe_id == recipe.id
        ).all()

        ingredients = []
        for recipe_ingredient in recipe_ingredients:
            ingredient = db.query(models.Ingredient).filter(
                models.Ingredient.id == recipe_ingredient.Ingredient_id
            ).first()
            if ingredient:
                ingredients.append(
                    IngredientInfo(name=ingredient.name, quantity=recipe_ingredient.currentQuantity)
                )

        # Append recipe details to the list
        all_recipes.append(
            RecipeViewResponse(
                id=recipe.id,
                name=recipe.name,
                description=recipe.description,
                product_type=product_type_name,
                ingredients=ingredients
            )
        )

    return all_recipes


@router.put("/recipe/update/{recipe_id}", response_model=RecipeViewResponse)
async def update_recipe(recipe_id: int, recipe_data: BaseRecipeUpdate, db: db_dependency):
    # Fetch the recipe
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Update recipe name and description if provided
    if recipe_data.name:
        recipe.name = recipe_data.name
    if recipe_data.description:
        recipe.description = recipe_data.description

    # Update product type if provided
    if recipe_data.product_name:
        product_type = db.query(models.ProductType).filter(models.ProductType.name == recipe_data.product_name).first()
        if not product_type:
            product_type = models.ProductType(name=recipe_data.product_name, code=recipe_data.product_name[:4].upper(),
                                              batchSize=0, expireDuration=0)
            db.add(product_type)
            db.commit()
            db.refresh(product_type)

        # Update recipe_has_producttype
        recipe_product_type = db.query(models.Recipe_has_producttype).filter(
            models.Recipe_has_producttype.Recipe_id == recipe.id).first()
        if recipe_product_type:
            recipe_product_type.ProductType_id = product_type.id
        else:
            recipe_product_type = models.Recipe_has_producttype(Recipe_id=recipe.id, ProductType_id=product_type.id)
            db.add(recipe_product_type)

    # Update ingredients
    if recipe_data.ingredients:
        existing_ingredients = {ri.Ingredient_id: ri.quantity for ri in db.query(models.RecipeHasIngredient).filter(
            models.RecipeHasIngredient.Recipe_id == recipe.id)}

        for ingredient_data in recipe_data.ingredients:
            # Check if ingredient already exists
            ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data.name).first()
            if not ingredient:
                ingredient = models.Ingredient(name=ingredient_data.name, currentQuantity=0, description="")
                db.add(ingredient)
                db.commit()
                db.refresh(ingredient)

            # If ingredient is new to this recipe, add it
            if ingredient.id not in existing_ingredients:
                recipe_ingredient = models.RecipeHasIngredient(
                    Recipe_id=recipe.id,
                    Ingredient_id=ingredient.id,
                    quantity=ingredient_data.quantity
                )
                db.add(recipe_ingredient)
            else:
                # Update quantity if different
                recipe_ingredient = db.query(models.RecipeHasIngredient).filter(
                    models.RecipeHasIngredient.Recipe_id == recipe.id,
                    models.RecipeHasIngredient.Ingredient_id == ingredient.id
                ).first()
                if recipe_ingredient.quantity != ingredient_data.quantity:
                    recipe_ingredient.quantity = ingredient_data.quantity

            # Remove the ingredient from the tracking dictionary if it's still part of the recipe
            existing_ingredients.pop(ingredient.id, None)

        # Remove any ingredients that are no longer needed
        for ingredient_id in existing_ingredients:
            db.query(models.RecipeHasIngredient).filter(
                models.RecipeHasIngredient.Recipe_id == recipe.id,
                models.RecipeHasIngredient.Ingredient_id == ingredient_id
            ).delete()

    # Commit all changes
    db.commit()

    # Fetch updated recipe with related data
    return await view_recipe(recipe_id, db)