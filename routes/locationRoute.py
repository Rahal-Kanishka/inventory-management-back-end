from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from typing import Annotated, List
from classes.classes import LocationCreate, LocationUpdate, LocationResponse
from fastapi import HTTPException



from models import models  # Assuming Location model is defined here
from utils.database import SessionLocal  # Database session dependency

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency annotation for session
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/location/list", response_model=List[LocationResponse])
async def get_all_locations(db: db_dependency):
    locations = db.query(models.Location).all()
    return locations


@router.get("/location/{id}", response_model=LocationResponse)
async def get_location_by_id(id: int, db: db_dependency):
    location = db.query(models.Location).filter(models.Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.get("/location/users/all", summary='Get all locations with assigned users')
async def get_all_locations_with_users(db: db_dependency):
    return db.query(models.Location).options(joinedload(models.Location.users)).all()


@router.post("/location/add", response_model=LocationResponse)
async def add_location(db: db_dependency, location_data: LocationCreate):
    new_location = models.Location(**location_data.dict())
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


@router.put("/location/update/{id}", response_model=LocationResponse)
async def update_location(id: int, db: db_dependency, location_data: LocationUpdate):
    location = db.query(models.Location).filter(models.Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    for key, value in location_data.dict().items():
        setattr(location, key, value)

    db.commit()
    db.refresh(location)
    return location


@router.delete("/location/delete/{id}")
async def delete_location(id: int, db: db_dependency):
    location = db.query(models.Location).filter(models.Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()
    return {"message": "Location deleted successfully"}
