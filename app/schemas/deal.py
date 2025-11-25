from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from datetime import datetime
from app.models.models import DealStatus, DealStage
from app.schemas import PageParams


class DealCreate(BaseModel):
    contact_id: int
    title: str
    amount: Annotated[
        Decimal, Field(max_digits=12, decimal_places=2)
    ] = Decimal(0)
    currency: str = "USD"


class DealPatch(BaseModel):
    status: Optional[DealStatus]
    stage: Optional[DealStage]
    title: Optional[str]
    amount: Optional[
        Annotated[Decimal, Field(max_digits=12, decimal_places=2)]
    ]


class DealOut(BaseModel):
    id: int
    title: str
    amount: Annotated[
        Decimal, Field(max_digits=12, decimal_places=2)
    ]
    currency: str
    status: DealStatus
    stage: DealStage
    contact_id: int
    owner_id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class ConfigDict:
        from_attributes = True


class DealsListOut(BaseModel):
    items: List[DealOut]
    total: int


class DealFilterQuery(PageParams):
    status: Optional[List[str]]
    stage: Optional[str]
    customer_name: Optional[str]
    min_amount: Optional[float]
    max_amount: Optional[float]
    owner_id: Optional[int]
    order_by: str = "created_at"
    order: str = "desc"
