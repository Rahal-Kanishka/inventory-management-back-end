from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Annotated, Optional, List

from models import models
from classes.classes import CreateProduct
from models.models import Recipe, Product
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


@router.get("/product/all")
async def getAllProducts(db: db_dependency):
    return (db.query(models.Product)
            .options(joinedload(models.Product.recipe))
            .all())


@router.post("/product/add")
async def addProduct(db: db_dependency, createProduct: CreateProduct):
    recipe = db.query(Recipe).filter(Recipe.id == createProduct.Recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_product = Product(**createProduct.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    # return data

    return (db.query(models.Product)
            .options(joinedload(models.Product.recipe))
            .filter(Product.id == db_product.id)
            .first())
