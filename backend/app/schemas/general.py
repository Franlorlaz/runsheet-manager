from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


# Mixin for timestamp fields
class TimestampMixin(SQLModel):
    # Make timestamps optional at the Pydantic level so creating models
    # doesn't require providing them; the DB will fill them using
    # server_default=func.now().
    created_at: datetime | None = Field(
        default=datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    updated_at: datetime | None = Field(
        default=datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
