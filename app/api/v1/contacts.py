from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user, get_current_org
from app.repositories.contact_repo import ContactRepository
from app.repositories.deal_repo import DealRepository
from app.services.contact_service import ContactService
from app.schemas.contact import ContactCreate, ContactOut, ContactQueryParams
from app.services.permission_service import is_owner

contacts_router = APIRouter(prefix="/contacts", tags=["contacts"])


@contacts_router.get("", response_model=list[ContactOut])
async def list_contacts(
    query: Annotated[ContactQueryParams, Query()],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """List contacts for the current organization."""
    repo = ContactRepository(db)
    ffilters = {}
    if query.search:
        ffilters["name"] = query.search
    if query.owner_id and is_owner(db, current_user.id, current_org.id):
        ffilters["owner_id"] = query.owner_id
    contacts = await repo.list_by_org(
        current_org.id,
        offset=(query.page - 1) * query.page_size,
        limit=query.page_size,
        filters=ffilters,
    )
    return contacts


@contacts_router.post(
    "", response_model=ContactOut, status_code=201
)
async def create_contact(
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """Create a new contact in the current organization."""
    svc = ContactService(ContactRepository(db))
    contact = await svc.create(
        owner_id=current_user.id,
        org_id=current_org.id,
        payload=payload,
    )
    return contact


@contacts_router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """Delete a contact by ID."""
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get(contact_id)

    if not contact or contact.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Contact not found")

    svc = ContactService(contact_repo)
    await svc.delete(contact, DealRepository(db))
    return
