import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.enums.step_system import StepSystem


# Shared properties
class StepProcessBase(SQLModel):
    title: str | None = None
    details: str | None = None
    system: StepSystem | None = None
    machine_time: float | None = None
    engineer_time: float | None = None
    date_completed: datetime | None = None
    engineer_id: uuid.UUID | None = None


# Properties to receive via API on creation
class StepProcessCreate(StepProcessBase):
    pass


# Properties to receive via API on update
class StepProcessUpdate(StepProcessBase):
    pass
