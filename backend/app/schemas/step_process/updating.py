import uuid
from datetime import datetime

from sqlmodel import SQLModel

from app.enums.step_system import StepSystem


# Properties to receive via API on creation
class StepProcessUpdate(SQLModel):
    title: str | None
    details: str | None
    system: StepSystem | None
    machine_time: float | None
    engineer_time: float | None
    date_completed: datetime | None
    engineer_id: uuid.UUID | None
