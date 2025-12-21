from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from .user_base import UserBase


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)
    updated_at: datetime | None = Field(default=datetime.now(timezone.utc))


class UserUpdateMe(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    updated_at: datetime | None = Field(default=datetime.now(timezone.utc))


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
