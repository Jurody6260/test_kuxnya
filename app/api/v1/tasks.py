from typing import Annotated
from app.db.base import get_db
from app.repositories.deal_repo import DealRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskOut, TaskQueryParams
from app.services.task_service import TaskService
from app.deps import get_current_user, get_current_org
from fastapi import APIRouter, Depends, Query

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@tasks_router.get("", response_model=list[TaskOut])
async def list_tasks(
    query: Annotated[TaskQueryParams, Query()],
    user=Depends(get_current_user),
    org=Depends(get_current_org),
    db=Depends(get_db),
):
    """List tasks for the current organization."""
    repo = TaskRepository(db)
    return await repo.list_by_org(org_id=org.id, **query.model_dump())


@tasks_router.post("", response_model=TaskOut)
async def create_task(
    payload: TaskCreate,
    user=Depends(get_current_user),
    org=Depends(get_current_org),
    db=Depends(get_db),
):
    """Create a new task in the current organization."""
    task_repo = TaskRepository(db)
    deal_repo = DealRepository(db)
    service = TaskService(task_repo, deal_repo)
    return await service.create(user, org.id, payload)
