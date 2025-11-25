from fastapi import HTTPException
from app.repositories.activity_repo import ActivityRepository
from app.repositories.deal_repo import DealRepository
from app.schemas.activity import ActivityCreate  # ожидаем существование


class ActivityService:
    def __init__(self, repo: ActivityRepository):
        self.repo = repo

    async def create(
        self, user, deal_id, payload: ActivityCreate
    ):
        # Простая бизнес логика: участники могут создавать активности
        # только для своих сделок/задач
        if getattr(user, "role", "member") == "member":
            # Проверка deal
            deal_repo = DealRepository(self.repo.session)
            deal = await deal_repo.get(deal_id)
            if not deal or deal.owner_id != user.id:
                raise HTTPException(
                    403,
                    "members can create activity only for their own deals",
                )

        return await self.repo.create_from_payload(
            author_id=user.id,
            **payload.model_dump(),
        )
