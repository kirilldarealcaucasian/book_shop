import datetime
from bcrypt import hashpw, gensalt, checkpw
from fastapi import HTTPException, status


from auth.config.auth_config import conf
from datetime import timedelta
from .schemas.token_schema import AccessToken, TokenPayload
from main.schemas import RegisterUserS
import jwt



def encode_jwt(
        payload: dict,
        private_key: str = conf.JWT_PRIVATE_KEY.read_text(),
        algorithm: str = conf.JWT_ENCODE_ALGORITHM,
        expire_timedelta: timedelta | None = None,
        expire_minutes: int = conf.ACCESS_TOKEN_EXPIRES_IN,
) -> AccessToken:
    payload_copy = payload.copy()
    now = datetime.datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    payload_copy.update(iat=now, exp=expire)

    token: str = jwt.encode(
        payload=payload_copy,
        key=private_key,
        algorithm=algorithm
    )
    return AccessToken(token=token)


def decode_jwt(
        token: str | bytes,
        algorithm: str = conf.JWT_DECODE_ALGORITHM,
        public_key: str = conf.JWT_PUBLIC_KEY.read_text()
) -> dict:
    try:
        return jwt.decode(jwt=token, algorithms=algorithm, key=public_key)
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(detail="Token has been expired",
                            status_code=status.HTTP_401_UNAUTHORIZED
                            )


def create_token(
        data: TokenPayload,
        expire_timedelta: timedelta | None = None
) -> AccessToken:
        payload = {
            "sub": data.email,
            "is_admin": data.is_admin
        }
        token = encode_jwt(payload=payload, expire_timedelta=expire_timedelta)
        return token


def hash_password(password: str, salt: str = conf.SALT) -> str:
    password_to_bytes = password.encode("utf-8")
    hashed_password = hashpw(password_to_bytes, salt.encode("utf-8"))
    return hashed_password.decode()


def validate_password(password: str, hashed_password: str) -> bool:
    if not (is_password_correct := checkpw(password.encode(), hashed_password.encode())
    ):
        raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Wrong password"
        )
    return is_password_correct
