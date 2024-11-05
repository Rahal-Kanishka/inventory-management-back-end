from typing import Annotated

from fastapi import Depends, APIRouter
from requests import Session

from models import models
from utils.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# annotation for dependency injection
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/order/all")
async def get_all_recipes(db: db_dependency):
    return db.query(models.Order).all()