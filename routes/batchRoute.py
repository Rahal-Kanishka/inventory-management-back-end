from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Annotated, List

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

@router.get("/batch/all", response_model=List[BaseBatch])
async def get_all_batches(db: db_dependency):
    return db.query(models.Batch).all()


@router.post("/batch/add", response_model=BaseBatch)
async def create_batch(db: db_dependency, batch_data: BaseBatchCreate):
    db_batch = models.Batch(**batch_data.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


@router.put("/batch/edit/{id}", response_model=BaseBatch)
async def update_batch(id: int, db: db_dependency, batch_data: BaseBatchCreate):
    batch = db.query(models.Batch).filter(models.Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    for field, value in batch_data.dict().items():
        setattr(batch, field, value)

    db.commit()
    db.refresh(batch)
    return batch


@router.delete("/batch/delete/{id}")
async def delete_batch(id: int, db: db_dependency):
    batch = db.query(models.Batch).filter(models.Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    db.delete(batch)
    db.commit()
    return {"message": "Batch deleted successfully"}

