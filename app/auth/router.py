from datetime import timedelta
from typing import Annotated

from decouple import config
from fastapi import Depends, status, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.models import Token
from app.auth.service import authenticate_user, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:

    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Access token expiration
    access_token_expires = timedelta(
        minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default=15))
    )

    # The JWT "sub" must be the username
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")
