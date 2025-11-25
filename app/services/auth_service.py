from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import RoleEnum
from app.repositories.user_repo import UserRepository
from app.repositories.org_repo import OrgRepository
from app.core.security import (
    PasswordHasher,
    TokenService,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrgRepository(db)
        self.tokens = TokenService()
        self.hasher = PasswordHasher()

    async def register(
        self, email: str, password: str, name: str, organization_name: str
    ):
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=409, detail="Email already registered"
            )

        password_hash = self.hasher.hash(password)
        user = await self.user_repo.create_from_payload(
            email=email, hashed_password=password_hash, name=name
        )

        org = await self.org_repo.create_from_payload(name=organization_name)
        await self.org_repo.add_member(org.id, user.id, role=RoleEnum.owner)

        await self.db.commit()

        access = self.tokens.create_access_token(user.id)
        refresh = self.tokens.create_refresh_token(user.id)
        return {
            "access": access,
            "refresh": refresh,
            "user_id": user.id,
            "organization_id": org.id,
        }

    async def login(
        self,
        email: str,
        password: str,
    ):
        user = await self.user_repo.get_by_email(email)
        user = authenticate_user(user, password, self.hasher)

        access = self.tokens.create_access_token(user.id)
        refresh = self.tokens.create_refresh_token(user.id)
        return {"access": access, "refresh": refresh, "user_id": user.id}


def authenticate_user(user, password: str, hasher: PasswordHasher):
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not hasher.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
