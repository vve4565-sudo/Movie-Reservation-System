import logging
from typing import Annotated
from uuid import UUID

from api.Depends import get_auth_service
from config.security import decode_token, get_access_token, get_refresh_token
from exceptions.auth import UserAlreadyExists, UserNotExists, WrongPassword
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jwt import ExpiredSignatureError
from schemas.auth import AuthCreds, FullCredentials, OutputUser
from service.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
lg = logging.getLogger(__name__)


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    credentials: FullCredentials,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> OutputUser:

    lg.info("Registration attempt for email=%s", credentials.email)

    try:
        user = await auth_service.register_user(credentials)
    except UserAlreadyExists as e:
        lg.warning(
            "Registration failed: user already exists, email=%s", credentials.email
        )

        raise HTTPException(status.HTTP_403_FORBIDDEN, "User already exists")

    access_token = await get_access_token(user.id)
    refresh_token = await get_refresh_token(user.id)

    response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie(
        "refresh_token",
        refresh_token,
        secure=True,
        httponly=True,
        samesite="none",
    )

    lg.info("Registration succeeded for user_id=%s", user.id)

    return user


@router.post("/login")
async def login(
    credentials: AuthCreds,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> OutputUser:

    lg.info("Login attempt for email=%s", credentials.email)

    try:
        user = await auth_service.authenticate_user(credentials)

    except UserNotExists as e:
        lg.warning(
            "Login failed: user not exists, email=%s",
            credentials.email,
            extra={"email": credentials.email},
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User not exists")

    except WrongPassword as e:
        lg.warning(
            "Login failed: wrong password, email=%s",
            credentials.email,
            extra={"email": credentials.email},
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Wrong password")

    access_token = await get_access_token(user.id)
    refresh_token = await get_refresh_token(user.id)

    response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie(
        "refresh_token",
        refresh_token,
        secure=True,
        httponly=True,
        samesite="none",
    )

    lg.info("Login succeeded for user_id=%s", user.id)

    return user


@router.get("/logout")
async def logout(response: Response):

    lg.info("Logout request received")

    response.headers["Authorization"] = "Bearer "
    response.delete_cookie("refresh_token")
    return


@router.get("/refresh")
async def refresh_access_token(request: Request, response: Response):

    lg.info("Token refresh request received")

    old_refresh_token = request.cookies.get("refresh_token")
    if not old_refresh_token:
        lg.warning("Token refresh failed: refresh token missing")

        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "refresh token expired")
    try:
        decoded_token = await decode_token(old_refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="server error")
    if not decoded_token.get("header").get("refresh"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    uuid = UUID(decoded_token.get("payload").get("sub"))
    new_access_token = await get_access_token(uuid)
    new_refresh_token = await get_refresh_token(uuid)
    response.headers["Authorization"] = f"Bearer {new_access_token}"
    response.set_cookie(
        "refresh_token",
        new_refresh_token,
        secure=True,
        httponly=True,
        samesite="none",
    )

    lg.info("Token refresh succeeded for user_id=%s", uuid, extra={"id": uuid})
