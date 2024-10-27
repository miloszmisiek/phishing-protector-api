from typing import Union
from passlib.context import CryptContext # type: ignore
from jose import JWTError, jwt # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from app.server.models.auth import TokenData
from app.server.models.user import UserInDB
from app.server.database import user_collection
from decouple import config
from fastapi import Depends, HTTPException, status
from app.services.constants import AuthKeys, ExceptionMessages

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str):
        user_data = await user_collection.find_one({"username": username})
        return UserInDB(**user_data)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config(AuthKeys.SECRET.value), algorithm=config(AuthKeys.ALGORITHM.value))
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail=ExceptionMessages.INVALID_CREDENTIALS, headers={"X-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, config(AuthKeys.SECRET.value), algorithms=[config(AuthKeys.ALGORITHM.value)])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = await get_user(username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail=ExceptionMessages.INACTIVE_USER)

    return current_user
