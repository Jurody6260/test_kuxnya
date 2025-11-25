from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Any, Dict
from app.core.config import settings
from logging import getLogger


logger = getLogger(__name__)

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.exceptions.PyJWTError as e:
        logger.error(f"Token decode error: {e}")
        raise


class TokenService:
    def __init__(self, secret: str = settings.JWT_SECRET):
        self.secret = secret

    def create_access_token(
        self, subject: int, expires_minutes: int | None = None
    ) -> str:
        expire = datetime.now() + timedelta(
            minutes=(expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload = {"sub": str(subject), "exp": expire}
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, self.secret, algorithms=["HS256"])
        except jwt.exceptions.PyJWTError as e:
            logger.error(f"Token decode error: {e}")
            raise

    def create_refresh_token(
        self,
        subject: int,
        expires_days: int | None = None,
    ) -> str:
        expire = datetime.now() + timedelta(
            days=(expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        to_encode = {"sub": str(subject), "exp": expire}
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


class PasswordHasher:
    def hash(self, password: str) -> str:
        return _pwd.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return _pwd.verify(plain, hashed)
