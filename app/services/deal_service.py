from decimal import Decimal
from fastapi import HTTPException
from datetime import datetime
from app.repositories.deal_repo import DealRepository
from app.repositories.activity_repo import ActivityRepository
from app.repositories.contact_repo import ContactRepository
from app.models.models import Deal, DealStatus, DealStage, RoleEnum
from app.schemas.deal import DealPatch


class DealService:
    def __init__(
        self,
        deal_repo: DealRepository,
        activity_repo: ActivityRepository,
        contact_repo: ContactRepository,
    ):
        self.deal_repo = deal_repo
        self.activity_repo = activity_repo
        self.contact_repo = contact_repo

    async def create_deal(self, org_id: int, owner_id: int, payload) -> Deal:
        # Ensure contact exists and belongs to org
        contact = await self.contact_repo.get(payload.contact_id)
        if not contact or contact.organization_id != org_id:
            raise HTTPException(
                status_code=404, detail="Contact not found in organization"
            )

        deal = Deal(
            organization_id=org_id,
            contact_id=payload.contact_id,
            owner_id=owner_id,
            title=payload.title,
            amount=payload.amount,
            currency=payload.currency,
            status=DealStatus.new,
            stage=DealStage.qualification,
        )
        await self.deal_repo.create(deal)
        # create activity: deal_created
        await self.activity_repo.create_for(
            deal.id,
            author_id=owner_id,
            type_="deal_created",
            payload={"title": deal.title},
        )
        return deal

    async def patch_deal(
        self, current_user, membership, deal: Deal, patch: DealPatch
    ):
        # membership.role is enum or str (owner/admin/manager/member)
        role = membership.role if hasattr(membership, "role") else membership

        # member can update only own deals
        if role == RoleEnum.member:
            if deal.owner_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="members can update only their own deals",
                )

        # Update amount/title first if provided (affects won rule)
        if patch.amount is not None:
            deal.amount = patch.amount
        if patch.title is not None:
            deal.title = patch.title

        # Status change rule: cannot set won if amount <= 0
        if patch.status is not None:
            new_status = patch.status
            if new_status == DealStatus.won and (
                deal.amount is None or Decimal(deal.amount) <= Decimal(0)
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot set status won when amount <= 0",
                )
            old_status = deal.status
            if old_status != new_status:
                deal.status = new_status
                await self.deal_repo.update(deal)
                await self.activity_repo.create_for(
                    deal.id,
                    author_id=current_user.id,
                    type_="status_changed",
                    payload={
                        "from": old_status.value,
                        "to": new_status.value,
                        "at": datetime.now().isoformat(),
                    },
                )

        # Stage change: forbid rollback for non-admin/owner
        if patch.stage is not None:
            new_stage = patch.stage
            order = [s for s in DealStage]
            curr_index = order.index(deal.stage)  # type: ignore
            new_index = order.index(new_stage)
            if new_index < curr_index and role not in (
                RoleEnum.admin,
                RoleEnum.owner,
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Stage rollback forbidden for your role",
                )
            if new_index > curr_index:
                old_stage = deal.stage
                deal.stage = new_stage
                await self.deal_repo.update(deal)
                await self.activity_repo.create_for(
                    deal.id,
                    author_id=current_user.id,
                    type_="stage_changed",
                    payload={
                        "from": old_stage.value,
                        "to": new_stage.value,
                        "at": datetime.now().isoformat(),
                    },
                )

        # Persist non-status/stage changes (title/amount already set)
        await self.deal_repo.update(deal)
        return deal

    async def delete_deal(self, current_user, membership, deal: Deal):
        role = membership.role if hasattr(membership, "role") else membership
        if role == RoleEnum.member and deal.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="members can delete only their own deals",
            )
        # Deleting deal: could add checks if tasks exist etc.
        await self.deal_repo.delete(deal)
        await self.activity_repo.create_for(
            deal.id,
            author_id=current_user.id,
            type_="deal_deleted",
            payload={},
        )
