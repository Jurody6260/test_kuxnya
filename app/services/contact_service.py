from fastapi import HTTPException
from app.repositories.contact_repo import ContactRepository
from app.repositories.deal_repo import DealRepository
from app.models.models import Contact


class ContactService:
    def __init__(
        self,
        contact_repo: ContactRepository,
    ):
        self.contact_repo = contact_repo

    async def create(self, owner_id: int, org_id: int, payload) -> Contact:
        c = Contact(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            owner_id=owner_id,
            organization_id=org_id,
        )
        return await self.contact_repo.create(c)

    async def delete(self, contact: Contact, deal_repo: DealRepository):
        # can't delete if deals exist
        deals = await deal_repo.list_by_contact(contact.id)
        if deals:
            raise HTTPException(
                status_code=409,
                detail="Contact has deals and cannot be deleted",
            )
        await self.contact_repo.delete(contact)
