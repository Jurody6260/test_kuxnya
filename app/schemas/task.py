from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TaskCreate(BaseModel):
    deal_id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]


class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[date]
    is_done: Optional[bool]


class TaskOut(BaseModel):
    id: int
    deal_id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]
    is_done: bool
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class TaskQueryParams(BaseModel):
    deal_id: Optional[int]
    only_open: Optional[bool]
    due_before: Optional[date]
    due_after: Optional[date]
