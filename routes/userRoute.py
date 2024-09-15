import base64
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

import models.models
from classes.classes import BaseRecipe, BaseIngredient, BaseUser
from sqlalchemy.orm import Session
from typing import Annotated

from utils.auth import get_current_user
from utils.database import SessionLocal
from utils.util import signJWT, get_hashed_password, verify_password, create_access_token, create_refresh_token

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# annotation for dependency injection
db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/login/", summary="Create access and refresh tokens for user")
async def login_user(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(models.models.User).filter(models.models.User.username == form_data.username).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username not found!")

    hashed_pass = user.password
    # if not verify_password(form_data.password, hashed_pass):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Incorrect email or password "
    #     )

    return {
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
    }


# async def get_current_user(token: str):
#     user = fake_decode_token(token)
#     return user


@router.post("/user")
async def create_user(new_user: BaseUser, db: db_dependency):
    # check if the username already exists
    user = db.query(models.models.User).filter(models.models.User.id == new_user.username).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists")
    # creating a new user
    db_user = models.models.User(**new_user.dict())
    db_user.password = get_hashed_password(db_user.password)
    db_user.created_at = datetime.now()
    db.add(db_user)
    db.commit()
    return db_user


@router.get('/me', summary='Get details of currently logged in user')
async def get_me(user: models.models.User = Depends(get_current_user)):
    return user


@router.get("/users/me")
async def read_users_me(current_user: Annotated[models.models.User, Depends(get_current_user)]):
    return current_user


def fake_decode_token(token):
    return models.User(
        username=token + "fakedecoded", email="john@example.com", name="John Doe"
    )
