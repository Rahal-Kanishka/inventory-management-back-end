from typing import Union, Any, Annotated
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

import models.models
from utils.database import SessionLocal
from utils.util import JWT_ALGORITHM, JWT_SECRET


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# annotation for dependency injection
db_dependency = Annotated[Session, Depends(get_db)]

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


async def get_current_user(db: db_dependency, token: str = Depends(reuseable_oauth)) -> any:
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        # token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(payload['exp']) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print('payload sub: ', payload['sub'])
    # extract user
    user = db.query(models.models.User).filter(models.models.User.username == payload['sub']).first()
    # user: Union[dict[str, Any], None] = db_dependency.get(payload['sub'], None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user
