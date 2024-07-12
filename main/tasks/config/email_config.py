from pydantic_settings import BaseSettings, SettingsConfigDict
# from main.tasks.config.get_email_data import(
# SMTP_HOST,
# SMTP_PORT,
# SMTP_USER,
# SMTP_PASS,
# )
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class EmailSettings(BaseSettings):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    model_config = SettingsConfigDict(env_file=".env")


email_settings = EmailSettings()