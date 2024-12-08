from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Annotated
from utils.database import SessionLocal
import models.models
from datetime import datetime

# Create API router
router = APIRouter()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/dashboard")
async def get_dashboard_data(db: db_dependency):
    """
    API to fetch dashboard data:
    - Total Batches Made
    - Number of Products
    - Number of Ingredients
    - Number of GRNs Issued
    - Number of Orders Received
    - Number of Users
    - Number of Locations
    - Number of Expired Batches
    """

    # 'Batch' count
    total_batches = db.query(func.count(models.models.Batch.id)).scalar()

    # 'Product' count
    total_products = db.query(func.count(models.models.Product.id)).scalar()

    # 'Ingredient' count
    total_ingredients = db.query(func.count(models.models.Ingredient.id)).scalar()

    # 'GRN' count
    total_grns = db.query(func.count(models.models.GRN.id)).scalar()

    # 'Order' count
    total_orders = db.query(func.count(models.models.Order.id)).scalar()

    # 'User' count
    total_users = db.query(func.count(models.models.User.id)).scalar()

    # 'Location' count
    total_locations = db.query(func.count(models.models.Location.id)).scalar()

    # 'Expired Batch' count
    expired_batches = db.query(func.count(models.models.Batch.id)).filter(
        models.models.Batch.dateOfExpiry < datetime.utcnow()
    ).scalar()

    return {
        "totalBatches": total_batches or 0,
        "totalProducts": total_products or 0,
        "totalIngredients": total_ingredients or 0,
        "totalGRNs": total_grns or 0,
        "totalOrders": total_orders or 0,
        "totalUsers": total_users or 0,
        "totalLocations": total_locations or 0,
        "expiredBatches": expired_batches or 0,
    }