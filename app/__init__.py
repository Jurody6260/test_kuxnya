from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.v1 import apiv1_router
from app.core.config import settings
from app.db.base import Base, async_engine


@asynccontextmanager  # type: ignore
async def on_startup(app: FastAPI):
    # Create database tables (for demo purposes).
    # In production use Alembic migrations.
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=on_startup,
    swagger_ui_parameters={"persistAuthorization": True},
)
app.include_router(apiv1_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    text = """
    # Kuxnya-CRM API


    Документация: все запросы проходят в контексте организации через заголовок
    `X-Organization-Id`.


    Auth flow:
    - POST /api/v1/auth/register — регистрирует пользователя
    и первую организацию
    - POST /api/v1/auth/login — логин


    Роли: owner, admin, manager, member — подробнее в описании сервиса.
    """

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=text,
        routes=app.routes,
    )

    # добавляем security схемы
    # openapi_schema.setdefault("components", {})
    # openapi_schema["components"].setdefault("securitySchemes", {})

    # openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
    #     "type": "http",
    #     "scheme": "bearer",
    #     "bearerFormat": "JWT",
    # }

    # глобальная авторизация
    # openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema



app.openapi = custom_openapi
