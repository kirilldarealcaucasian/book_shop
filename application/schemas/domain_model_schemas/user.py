from datetime import datetime, date
from pydantic import BaseModel


class UserS(BaseModel):
    first_name: str
    last_name: str
    gender: str
    email: str | None
    hashed_password: str | bytes | None
    registration_date: datetime | None
    role_name: str | None
    date_of_birth: date | None