from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.deps import get_db, get_current_user, get_current_org
from app.repositories.deal_repo import DealRepository
from app.repositories.activity_repo import ActivityRepository
from app.repositories.contact_repo import ContactRepository
from app.services.deal_service import DealService
from app.schemas.deal import (
    DealCreate,
    DealFilterQuery,
    DealOut,
    DealPatch,
    DealsListOut,
)

deals_router = APIRouter(prefix="/deals", tags=["Deals"])


@deals_router.post(
    "",
    response_model=DealOut,
    status_code=201,
    responses={
        400: {"description": "Bad Request"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)
async def create_deal(
    payload: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """Create a new deal in the current organization."""
    # current_org is membership object or has organization_id and role
    org_id = (
        current_org.organization_id
        if hasattr(current_org, "organization_id")
        else current_org.id
    )
    # repos/services
    deal_repo = DealRepository(db)
    activity_repo = ActivityRepository(db)
    contact_repo = ContactRepository(db)
    svc = DealService(deal_repo, activity_repo, contact_repo)

    # members: manager/member can create;
    # members can create only own deals (owner_id = current_user.id)
    # create_deal sets owner=current_user.id
    deal = await svc.create_deal(
        org_id=org_id, owner_id=current_user.id, payload=payload
    )
    await db.commit()
    return deal


@deals_router.get("", response_model=DealsListOut)
async def list_deals(
    query: Annotated[DealFilterQuery, Query()],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """List deals for the current organization."""
    org_id = (
        current_org.organization_id
        if hasattr(current_org, "organization_id")
        else current_org.id
    )
    repo = DealRepository(db)
    offset = (query.page - 1) * query.page_size
    items = await repo.list_by_org(
        org_id=org_id,
        status=query.status or None,
        stage=query.stage,
        min_amount=query.min_amount,
        max_amount=query.max_amount,
        owner_id=query.owner_id,
        offset=offset,
        limit=query.page_size,
        order_by=query.order_by,
        order=query.order,
    )
    # naive total (should be optimized)
    total = len(items)
    return {"items": items, "total": total}


@deals_router.get("/{deal_id}", response_model=DealOut)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """Get a specific deal by ID."""
    repo = DealRepository(db)
    deal = await repo.get(deal_id)
    if not deal or deal.organization_id != (
        current_org.organization_id
        if hasattr(current_org, "organization_id")
        else current_org.id
    ):
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@deals_router.patch("/{deal_id}", response_model=DealOut)
async def patch_deal(
    deal_id: int,
    patch: DealPatch,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """Update a specific deal by ID."""
    repo = DealRepository(db)
    activity_repo = ActivityRepository(db)
    contact_repo = ContactRepository(db)
    svc = DealService(repo, activity_repo, contact_repo)

    deal = await repo.get(deal_id)
    if not deal or deal.organization_id != (
        current_org.organization_id
        if hasattr(current_org, "organization_id")
        else current_org.id
    ):
        raise HTTPException(status_code=404, detail="Deal not found")

    # membership object provides role and organization_id
    membership = current_org
    updated = await svc.patch_deal(
        current_user=current_user,
        membership=membership,
        deal=deal,
        patch=patch,
    )
    await db.commit()
    return updated


@deals_router.delete("/{deal_id}", status_code=204)
async def delete_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """Delete a specific deal by ID."""
    repo = DealRepository(db)
    activity_repo = ActivityRepository(db)
    svc = DealService(repo, activity_repo, ContactRepository(db))
    deal = await repo.get(deal_id)
    if not deal or deal.organization_id != (
        current_org.organization_id
        if hasattr(current_org, "organization_id")
        else current_org.id
    ):
        raise HTTPException(status_code=404, detail="Deal not found")
    await svc.delete_deal(
        current_user=current_user, membership=current_org, deal=deal
    )
    await db.commit()
    return None
