import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload
from typing import Annotated
from sqlalchemy import select, func
from utils.database import SessionLocal
from models.models import Order, Product, Batch
from classes.classes import CreateOrder, UpdateOrder


# Configure logging
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
db_dependency = Annotated[SessionLocal, Depends(get_db)]

@router.get("/order/all")
async def getAllOrders(db: db_dependency):
    batch_name_subq = (
        select(Batch.name)
        .where(Batch.product_id == Order.Product_id)
        .order_by(Batch.productionDate.asc())
        .limit(1)
        .scalar_subquery()
    )

    orders = (db.query(
                Order.id,
                Order.name,
                Order.quantity,
                batch_name_subq.label('batch_name')
              )
              .all())

    results = []
    for o in orders:
        results.append({
            "id": o[0],
            "name": o[1],
            "quantity": o[2],
            "batch_name": o[3] if o[3] is not None else None
        })
    return results


@router.post("/order/add")
async def addOrder(db: db_dependency, createOrder: CreateOrder):
    # Check if product_id exists
    product = db.query(Product).filter(Product.id == createOrder.Product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Find a batch that can fulfill the requested quantity
    batch = (db.query(Batch)
             .filter(Batch.product_id == createOrder.Product_id,
                     Batch.availableQuantity >= createOrder.quantity)
             .order_by(Batch.productionDate.asc())
             .first()
             )

    if not batch:
        raise HTTPException(status_code=409, detail="Not enough available quantity to fulfill the order")

    remaining_quantity = batch.availableQuantity - createOrder.quantity
    if remaining_quantity < 0:
        raise HTTPException(status_code=409, detail="Fulfilling this order would leave no available quantity")

    # Create the Order using the same field names
    db_order = Order(**createOrder.dict())
    db.add(db_order)

    # Update the batch available quantity
    batch.availableQuantity = remaining_quantity

    db.commit()
    db.refresh(db_order)

    return {
        "id": db_order.id,
        "name": db_order.name,
        "quantity": db_order.quantity,
        "product_id": db_order.Product_id,
        "batch_name": batch.name
    }