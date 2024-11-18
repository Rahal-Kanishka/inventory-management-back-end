from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from typing import Annotated, List

from starlette import status

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


@router.get("/location/user/{user_id}", summary="filter assigned Locations based on given user")
async def get_locations_by_user(db: db_dependency, user_id: int):
    user = db.query(models.Location).filter(models.Location.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found!")

    # Get users assigned to location
    return db.query(models.Location).join(models.Location.users).filter(models.User.id == user_id).all()


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


@router.delete("/location/remove_user/{user_id}/{location_id}", summary="remove user from a locationr")
async def remove_user_from_location(db: db_dependency, user_id: int, location_id: int):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found!")

    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location not found!")

    location.users.remove(user)
    # Get users assigned to location
    db.add(location)
    db.commit()

    return (db.query(models.User)
            .join(models.User.locations)  # Join the locations relationship
            .filter(models.Location.id == location_id)  # Eager load locations if needed
            .all())


@router.put("/location/assign_user/{user_id}/{location_id}", summary="Assign location to a user")
async def assign_user_to_location(db: db_dependency, user_id: int, location_id: int):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found!")

    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location not found!")

    location.users.append(user)
    db.add(location)
    db.commit()
    return (db.query(models.User)
            .join(models.User.locations)  # Join the locations relationship
            .filter(models.Location.id == location_id)  # Eager load locations if needed
            .all())


async def get_location_with_assigned_users(db, location_id: int):
    return (db.query(models.Location)
            .options(joinedload(models.Location.users))
            .filter(models.Location.id == location_id)  # Join the locations relationship
            .first())