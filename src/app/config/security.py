import asyncio
from datetime import datetime, timezone
from uuid import UUID

import jwt
from config.config import config
from pwdlib import PasswordHash

password_hash: PasswordHash = PasswordHash.recommended()
dummy_hash: str = password_hash.hash("Meshuggah-Bleed")


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(password_hash.hash, password)


async def verify_password(plain_password: str, hash_password: str) -> bool:
    return password_hash.verify(plain_password, hash_password)


async def get_access_token(id: UUID):
    expire = datetime.now(timezone.utc) + config.ACCESS_TOKEN_EXPIRE
    data = {"sub": str(id), "exp": expire}
    access_token = jwt.encode(
        data,
        config.JWT_SECRET_KEY,
        config.CRYPT_ALGORITHM,
    )
    return access_token


async def get_refresh_token(id: UUID):
    expire = datetime.now(timezone.utc) + config.REFRESH_TOKEN_EXPIRE
    data = {"sub": str(id), "exp": expire}
    refresh_token = jwt.encode(
        data,
        config.JWT_SECRET_KEY,
        config.CRYPT_ALGORITHM,
    )
    return refresh_token
