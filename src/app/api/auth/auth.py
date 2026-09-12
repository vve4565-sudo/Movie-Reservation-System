from typing import Annotated

from api.Depends import get_auth_service
from config.security import get_access_token, get_refresh_token
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from schemas.auth import AuthCreds, FullCredentials, OutputUser
from service.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    credentials: FullCredentials,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> OutputUser:
    user = await auth_service.register_user(credentials)

    if not user:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User already exists")

    access_token = await get_access_token(user.id)
    refresh_token = await get_refresh_token(user.id)

    response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=30,
        secure=True,
        httponly=True,
    )

    return user


@router.post("/login")
async def login(
    credentials: AuthCreds,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> OutputUser:
    user = await auth_service.authenticate_user(credentials)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not exists")

    access_token = await get_access_token(user.id)
    refresh_token = await get_refresh_token(user.id)

    response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=30,
        secure=True,
        httponly=True,
    )
    return user


@router.get("/logout")
async def logout(response: Response):
    response.headers["Authorization"] = ""
    response.delete_cookie("refresh_token")
    return
