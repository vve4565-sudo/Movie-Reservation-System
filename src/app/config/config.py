from datetime import timedelta
from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_SCHEME: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PATH: str

    @computed_field
    @property
    def database_config(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.DATABASE_SCHEME,
            host=self.DATABASE_HOST,
            path=self.DATABASE_PATH,
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            port=self.DATABASE_PORT,
        )

    SUPERUSER_NAME: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE: timedelta = timedelta(minutes=60)
    REFRESH_TOKEN_EXPIRE: timedelta = timedelta(days=30)
    CRYPT_ALGORITHM: str = "HS256"


config = Config()
