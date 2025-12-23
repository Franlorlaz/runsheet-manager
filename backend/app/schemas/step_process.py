import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.enums.step_system import StepSystem


# Shared properties
class StepProcessBase(SQLModel):
    title: str = Field(default=None, max_length=255)


# Properties to receive via API on creation
class StepProcessCreate(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    details: str | None = Field(default=None, max_length=2048)
    system: StepSystem | None = Field(default=StepSystem.other)
    machine_time: float | None = Field(default=0.0)
    engineer_time: float | None = Field(default=0.0)
    date_completed: datetime | None = Field(default=None)
    engineer_id: uuid.UUID | None = Field(default=None)


# Properties to receive via API on update
class StepProcessUpdate(SQLModel):
    title: str | None = None
    details: str | None = None
    system: StepSystem | None = None
    machine_time: float | None = None
    engineer_time: float | None = None
    date_completed: datetime | None = None
    engineer_id: uuid.UUID | None = None
