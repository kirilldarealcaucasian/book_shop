from datetime import datetime, timedelta
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import FutureDatetime
from dotenv import load_dotenv
from dateparser import parse

__all__ = (
    "settings",
)

load_dotenv()


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST"]

    LOG_LEVEL: str
    LOGS_JOURNAL_PATH: str

    DB_USER: str
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

    RABBIT_USER: str
    RABBIT_PASSWORD: str
    Rabbit_HOST: str
    Rabbit_PORT: int

    SHOPPING_SESSION_DURATION: str
    @property
    def SHOPPING_SESSION_EXPIRATION_TIMEDELTA(self) -> timedelta:
        parsed_interval = parse(self.SHOPPING_SESSION_DURATION)
        reference_time = datetime.now()
        time_delta = parsed_interval - reference_time
        return timedelta(abs(time_delta.total_seconds()))

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def get_db_url(cls):
        if cls.MODE == "DEV":
            return f"postgresql+asyncpg://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_SERVER}:{cls.DB_PORT}/{cls.DB_NAME}"

        if cls.MODE == "TEST":
            return f"postgresql+asyncpg://{cls.TEST_POSTGRES_USER}:{cls.TEST_POSTGRES_PASSWORD}@{cls.TEST_POSTGRES_SERVER}:{cls.TEST_POSTGRES_PORT}/{cls.TEST_POSTGRES_DB}"


settings = Settings()
