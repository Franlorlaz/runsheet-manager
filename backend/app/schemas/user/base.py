import sqlalchemy as sa
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    is_reviewer: bool = Field(default=False, sa_column=sa.Column(sa.Boolean(), nullable=False, server_default=sa.false()))
    name: str | None = Field(default=None, max_length=255)
