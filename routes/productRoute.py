from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
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


@router.get("/product/all")
async def getAllProducts(db: db_dependency):
    return (db.query(models.Product)
            .options(joinedload(models.Product.recipe))
            .all())