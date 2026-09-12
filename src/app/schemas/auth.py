from typing import Literal

from database.models import Roles
from pydantic import BaseModel, ConfigDict, EmailStr


class Credentials(BaseModel):
    email: EmailStr
    nickname: str


class FullCredentials(Credentials):
    password: str


class HashedCredentials(Credentials):
    password_hash: str


class OutputUser(BaseModel):
    nickname: str
    email: EmailStr
    Role: Roles

    model_config = ConfigDict(from_attributes=True)


class AuthCreds(BaseModel):
    password: str
    email: EmailStr


class HashedAuthCreds(AuthCreds):
    hashed_password: str
    email: EmailStr
