from datetime import date
from fastapi import HTTPException
from app.models.models import Deal, User
from app.repositories.task_repo import TaskRepository
from app.repositories.deal_repo import DealRepository
from app.schemas.task import TaskCreate


class TaskService:
    def __init__(self, task_repo: TaskRepository, deal_repo: DealRepository):
        self.task_repo = task_repo
        self.deal_repo = deal_repo

    async def create(self, user: User, org_id: int, payload: TaskCreate):
        # due_date cannot be in the past
        if payload.due_date and payload.due_date < date.today():
            raise HTTPException(
                status_code=400, detail="due_date cannot be in the past"
            )

        deal: Deal | None = await self.deal_repo.get(payload.deal_id)
        if not deal or deal.organization_id != org_id:
            raise HTTPException(status_code=404, detail="Deal not found")

        return await self.task_repo.create_from_payload(
            user_id=user.id, org_id=org_id, **payload.model_dump()
        )
