from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent[3]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env", env_ignore_empty=True, env_file_encoding="utf-8"
    )

    DATABASE_SCHEME: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PATH: str

    @computed_field
    @property
    def database_config(self):
        return PostgresDsn.build(
            scheme=self.DATABASE_SCHEME,
            host=self.DATABASE_HOST,
            path=self.DATABASE_PATH,
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
        )


config = Config()
