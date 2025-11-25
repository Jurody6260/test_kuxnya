from typing import Annotated
from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import RegisterIn, LoginIn, TokenOut
from app.deps import get_db
from app.services.auth_service import AuthService


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=TokenOut)
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    """Register a new user and organization."""
    svc = AuthService(db)
    res = await svc.register(
        email=payload.email,
        password=payload.password,
        name=payload.name or "",
        organization_name=payload.organization_name,
    )
    return {
        "access_token": res["access"],
        "refresh_token": res["refresh"],
        "token_type": "bearer",
        "organization_id": res["organization_id"],
    }


@auth_router.post("/login", response_model=TokenOut)
async def login(
    payload: Annotated[LoginIn, Form()],
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a user and return access and refresh tokens."""
    svc = AuthService(db)
    res = await svc.login(
        email=payload.username,
        password=payload.password,
    )
    return {
        "access_token": res["access"],
        "refresh_token": res["refresh"],
        "token_type": "bearer",
    }
