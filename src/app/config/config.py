import sys
from datetime import timedelta
from enum import StrEnum
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

    BASE_STORAGE_URL: Path = ROOT_DIR / "storage"

    REDIS_PORT: int


class LOGGER_LEVEL(StrEnum):
    INFO = "INFO"
    DEBUG = "DEBUG"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    # Форматирование: определяем, какие поля из LogRecord попадут в JSON
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s %(lineno)d",
        },
    },
    # Обработчики: куда отправляем логи (по 12-Factor App — в stdout)
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json",
        },
    },
    # Корневой логгер
    "root": {
        "level": "INFO",
        "handlers": ["stdout"],
    },
}


config = Config()
