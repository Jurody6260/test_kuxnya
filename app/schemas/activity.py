from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class ActivityCreate(BaseModel):
    type: str = "comment"
    payload: dict


class ActivityOut(BaseModel):
    id: int
    deal_id: int
    author_id: Optional[int]
    type: str
    payload: Any
    created_at: datetime

    class ConfigDict:
        from_attributes: bool = True
