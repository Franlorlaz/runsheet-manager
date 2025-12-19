from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, SQLModel


# Mixin for timestamp fields
class TimestampMixin(SQLModel):  # type: ignore
    """Timestamp mixin.
    A mixin to add created_at and updated_at timestamp fields to a model.
    Make timestamps optional at the Pydantic level so creating models
    doesn't require providing them; the DB will fill them using
    server_default=func.now().
    """

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True)
        # server_default=func.now()  # Added manually in migrations
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=TIMESTAMP(timezone=True)
        # server_default=func.now()  # Added manually in migrations
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
