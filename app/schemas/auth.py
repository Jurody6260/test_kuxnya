from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str]
    organization_name: str


class LoginIn(BaseModel):
    username: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
