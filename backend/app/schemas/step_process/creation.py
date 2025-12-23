import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.enums.step_system import StepSystem


# Properties to receive via API on creation
class StepProcessCreate(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    details: str | None = Field(default=None, max_length=2048)
    system: StepSystem | None = Field(default=StepSystem.other)
    machine_time: float | None = Field(default=0.0)
    engineer_time: float | None = Field(default=0.0)
    date_completed: datetime | None = Field(default=None)
    engineer_id: uuid.UUID | None = Field(default=None)

    step_number: int = Field(default=0)
    runsheet_id: uuid.UUID = Field(foreign_key="runsheet.id", nullable=False, ondelete="CASCADE")
    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
