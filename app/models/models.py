from typing import List, Optional
import datetime as dt
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Enum,
    Numeric,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.base import Base
import enum


class RoleEnum(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    member = "member"


class DealStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    won = "won"
    lost = "lost"


class DealStage(str, enum.Enum):
    qualification = "qualification"
    proposal = "proposal"
    negotiation = "negotiation"
    closed = "closed"


# Было бы лучше разбить эти модели на несколько файлов,
# но для простоты они все в одном файле.


class Organization(Base):
    __tablename__ = "organizations"
    name: Mapped[str]
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization"
    )


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    name: Mapped[Optional[str]]
    organizations: Mapped[List["Organization"]] = relationship(
        "Organization", secondary="organization_members"
    )


class OrganizationMember(Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_org_user",
        ),
    )
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="members"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        )
    )
    user: Mapped["User"] = relationship("User")
    role: Mapped[enum.Enum] = mapped_column(
        Enum(RoleEnum),
        default=RoleEnum.member,
    )


class Contact(Base):
    __tablename__ = "contacts"
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str]
    email: Mapped[str]
    phone: Mapped[str]


class Deal(Base):
    __tablename__ = "deals"
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    amount = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(
        String(3), default="USD"
    )  # "USD", "EUR", etc.
    status: Mapped[enum.Enum] = mapped_column(
        Enum(DealStatus),
        default=DealStatus.new,
    )
    stage: Mapped[enum.Enum] = mapped_column(
        Enum(DealStage), default=DealStage.qualification
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        default=func.now(),
    )
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="deal")


class Task(Base):
    __tablename__ = "tasks"
    deal: Mapped["Deal"] = relationship("Deal", back_populates="tasks")
    deal_id: Mapped[int] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"),
    )
    title: Mapped[str]
    description: Mapped[str]
    due_date: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime(timezone=True),
    )
    is_done: Mapped[bool] = mapped_column(default=False)


class Activity(Base):
    __tablename__ = "activities"
    deal_id: Mapped[int] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"),
    )
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str]  # comment, status_changed, task_created, system
    payload = mapped_column(JSON)
