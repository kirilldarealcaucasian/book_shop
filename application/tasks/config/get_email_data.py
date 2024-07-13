from dotenv import load_dotenv
import os

load_dotenv()

SMTP_HOST: str = os.getenv("SMTP_HOST")
SMTP_PORT: int = int(os.getenv("SMTP_PORT"))
SMTP_USER: str = os.getenv("SMTP_USER")
SMTP_PASS: str = os.getenv("SMTP_PASS")