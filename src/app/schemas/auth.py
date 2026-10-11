from uuid import UUID

from pydantic import EmailStr

from app.database.models import Roles

from .base import Base


class Credentials(Base):
    email: EmailStr
    nickname: str


class FullCredentials(Credentials):
    password: str


class HashedCredentials(Credentials):
    password_hash: str


class OutputUser(Base):
    id: UUID
    nickname: str
    email: EmailStr
    role: Roles


class AuthCreds(Base):
    password: str
    email: EmailStr


class HashedAuthCreds(AuthCreds):
    hashed_password: str
    email: EmailStr
