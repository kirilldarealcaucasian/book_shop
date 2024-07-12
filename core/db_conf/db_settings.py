from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

__all__ = (
    "settings",
)

load_dotenv()


class DBSettings(BaseSettings):
    MODE: Literal["DEV", "TEST"]

    DB_USER: str
    LOG_LEVEL: str
    DB_PASSWORD: str
    DB_SERVER: str
    DB_PORT: int
    DB_NAME: str

    TEST_POSTGRES_USER: str
    TEST_POSTGRES_PASSWORD: str
    TEST_POSTGRES_SERVER: str
    TEST_POSTGRES_PORT: int
    TEST_POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def get_db_url(cls):
        if cls.MODE == "DEV":
            return f"postgresql+asyncpg://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_SERVER}:{cls.DB_PORT}/{cls.DB_NAME}"

        if cls.MODE == "TEST":
            return f"postgresql+asyncpg://{cls.TEST_POSTGRES_USER}:{cls.TEST_POSTGRES_PASSWORD}@{cls.TEST_POSTGRES_SERVER}:{cls.TEST_POSTGRES_PORT}/{cls.TEST_POSTGRES_DB}"


settings = DBSettings()



