from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.schemas import PageParams


class ContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]


class ContactOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    owner_id: int
    organization_id: int
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class ContactQueryParams(PageParams):

    search: Optional[str] = None
    owner_id: Optional[int] = None
