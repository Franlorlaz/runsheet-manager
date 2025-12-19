"""Data Base Models

Database table inferred from class name.
WARNING: server_default=sa.text('now()')  # Added manually in migrations when using TimestampMixin
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship

from app.enums.material import Material
from app.enums.runsheet_state import RunsheetState
from app.enums.sample_type import SampleType
from app.enums.step_system import StepSystem
from app.schemas.general import TimestampMixin
from app.schemas.item.item_base import ItemBase
from app.schemas.runsheet.runsheet_base import RunsheetBase
from app.schemas.sample.sample_base import SampleBase
from app.schemas.step_process.step_process_base import StepProcessBase
from app.schemas.user.user_base import UserBase


# USER
class User(TimestampMixin, UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# ITEM
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# SAMPLE
class Sample(TimestampMixin, SampleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    description: str | None = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=2048)

    exist: bool = Field(default=True)
    location: str | None = Field(default=None, max_length=255)
    type: SampleType = Field(default=SampleType.other, sa_column=SQLEnum(SampleType))
    material: Material = Field(default=Material.other, sa_column=SQLEnum(Material))


# RUNSHEET
class Runsheet(TimestampMixin, RunsheetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    material: Material = Field(default=Material.other, sa_column=SQLEnum(Material))
    description: str | None = Field(default=None, max_length=1024)
    state: RunsheetState = Field(default=RunsheetState.edit, sa_column=SQLEnum(RunsheetState))


# STEP PROCESS
class StepProcess(TimestampMixin, StepProcessBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    step_number: int = Field(default=0)
    details: str = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=2048)

    system: StepSystem = Field(default=StepSystem.other, sa_column=SQLEnum(StepSystem))
    machine_time: float = Field(default=0.0)
    engineer_time: float = Field(default=0.0)
    date_completed: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    completed: bool = Field(default=False)
    # user_engineer: FOREIGN KEY
