from app.core.config import settings
from fastapi import APIRouter
from .activity import activities_router
from .analytics import analytics_router
from .auth import auth_router
from .contacts import contacts_router
from .organizations import organizations_router
from .deals import deals_router
from .tasks import tasks_router


apiv1_router = APIRouter(prefix=f"{settings.API_V1_STR}")
apiv1_router.include_router(auth_router)
apiv1_router.include_router(organizations_router)
apiv1_router.include_router(contacts_router)
apiv1_router.include_router(deals_router)
apiv1_router.include_router(tasks_router)
apiv1_router.include_router(activities_router)
apiv1_router.include_router(analytics_router)
