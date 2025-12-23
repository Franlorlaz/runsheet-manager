"""Data Base Models

Database table inferred from class name.
WARNING: server_default=sa.text('now()')  # Added manually in migrations when using TimestampMixin
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, false
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel

from app.enums.material import Material
from app.enums.runsheet_state import RunsheetState
from app.enums.sample_type import SampleType
from app.enums.step_system import StepSystem
from app.schemas.general import TimestampMixin
from app.schemas.item import ItemBase
from app.schemas.runsheet import RunsheetBase
from app.schemas.sample import SampleBase
from app.schemas.step_process import StepProcessBase
from app.schemas.user import UserBase


# PIVOT TABLES
class SampleSupervisorLink(SQLModel, table=True):
    __tablename__ = "link_sample_supervisor"
    sample_id: uuid.UUID = Field(foreign_key="sample.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class SampleStepProcessLink(SQLModel, table=True):
    __tablename__ = "link_sample_step_process"
    sample_id: uuid.UUID = Field(foreign_key="sample.id", primary_key=True)
    step_process_id: uuid.UUID = Field(foreign_key="step_process.id", primary_key=True)
    completed: bool = Field(default=False, sa_column=Column(Boolean(), nullable=False, server_default=false()))


class RunsheetSampleLink(SQLModel, table=True):
    __tablename__ = "link_runsheet_sample"
    sample_id: uuid.UUID = Field(foreign_key="sample.id", primary_key=True)
    runsheet_id: uuid.UUID = Field(foreign_key="runsheet.id", primary_key=True)


# USER
class User(TimestampMixin, UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

    # Creation relationships
    created_samples: list["Sample"] = Relationship(back_populates="creator", cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[Sample.creator_id]"})
    created_runsheets: list["Runsheet"] = Relationship(back_populates="creator", cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[Runsheet.creator_id]"})
    created_step_processes: list["StepProcess"] = Relationship(back_populates="creator", cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[StepProcess.creator_id]"})

    # Relationships
    samples_supervised: list["Sample"] = Relationship(
        back_populates="supervisors",
        link_model=SampleSupervisorLink,
        sa_relationship_kwargs={
            "primaryjoin": "User.id==SampleSupervisorLink.user_id",
            "secondaryjoin": "Sample.id==SampleSupervisorLink.sample_id",
            "foreign_keys": "[SampleSupervisorLink.user_id, SampleSupervisorLink.sample_id]"
        }
    )
    runsheets_reviewed: list["Runsheet"] = Relationship(back_populates="reviewer", sa_relationship_kwargs={"foreign_keys": "[Runsheet.reviewer_id]"})
    assigned_step_processes: list["StepProcess"] = Relationship(back_populates="engineer", sa_relationship_kwargs={"foreign_keys": "[StepProcess.engineer_id]"})

    # String representation
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} name={self.name}>"


# ITEM
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
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

    # Relationships
    parent_sample_id: uuid.UUID | None = Field(default=None, foreign_key="sample.id", nullable=True)
    parent_sample: Optional["Sample"] = Relationship(back_populates="derived_samples", sa_relationship_kwargs={"remote_side": "Sample.id"})
    derived_samples: list["Sample"] = Relationship(back_populates="parent_sample", sa_relationship_kwargs={"cascade": "save-update"})

    supervisors: list["User"] = Relationship(
        back_populates="samples_supervised",
        link_model=SampleSupervisorLink,
        sa_relationship_kwargs={
            "primaryjoin": "Sample.id==SampleSupervisorLink.sample_id",
            "secondaryjoin": "User.id==SampleSupervisorLink.user_id",
            "foreign_keys": "[SampleSupervisorLink.sample_id, SampleSupervisorLink.user_id]"
        }
    )
    runsheets: list["Runsheet"] = Relationship(
        back_populates="samples",
        link_model=RunsheetSampleLink,
        sa_relationship_kwargs={
            "primaryjoin": "Sample.id==RunsheetSampleLink.sample_id",
            "secondaryjoin": "Runsheet.id==RunsheetSampleLink.runsheet_id",
            "foreign_keys": "[RunsheetSampleLink.sample_id, RunsheetSampleLink.runsheet_id]"
        }
    )
    step_processes: list["StepProcess"] = Relationship(
        back_populates="samples",
        link_model=SampleStepProcessLink,
        sa_relationship_kwargs={
            "primaryjoin": "Sample.id==SampleStepProcessLink.sample_id",
            "secondaryjoin": "StepProcess.id==SampleStepProcessLink.step_process_id",
            "foreign_keys": "[SampleStepProcessLink.sample_id, SampleStepProcessLink.step_process_id]"
        }
    )

    # Creation relationship
    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    creator: User | None = Relationship(back_populates="created_samples", sa_relationship_kwargs={"foreign_keys": "[Sample.creator_id]"})

    # String representation
    def __repr__(self) -> str:
        return f"<Sample id={self.id} name={self.name} type={self.type} exist={self.exist}>"


# RUNSHEET
class Runsheet(TimestampMixin, RunsheetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    material: Material = Field(default=Material.other, sa_column=SQLEnum(Material))
    description: str | None = Field(default=None, max_length=1024)
    state: RunsheetState = Field(default=RunsheetState.edit, sa_column=SQLEnum(RunsheetState))

    # Relationships
    reviewer_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL")
    reviewer: User | None = Relationship(back_populates="runsheets_reviewed", sa_relationship_kwargs={"foreign_keys": "[Runsheet.reviewer_id]"})
    step_processes: list["StepProcess"] = Relationship(back_populates="runsheet", cascade_delete=True)
    samples: list["Sample"] = Relationship(
        back_populates="runsheets",
        link_model=RunsheetSampleLink,
        sa_relationship_kwargs={
            "primaryjoin": "Runsheet.id==RunsheetSampleLink.runsheet_id",
            "secondaryjoin": "Sample.id==RunsheetSampleLink.sample_id",
            "foreign_keys": "[RunsheetSampleLink.runsheet_id, RunsheetSampleLink.sample_id]"
        }
    )

    # Creation relationship
    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    creator: User | None = Relationship(back_populates="created_runsheets", sa_relationship_kwargs={"foreign_keys": "[Runsheet.creator_id]"})

    # String representation
    def __repr__(self) -> str:
        return f"<Runsheet id={self.id} citic_id={self.citic_id} state={self.state}>"


# STEP PROCESS
class StepProcess(TimestampMixin, StepProcessBase, table=True):
    __tablename__ = "step_process"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    step_number: int = Field(default=0)
    details: str = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=2048)

    system: StepSystem = Field(default=StepSystem.other, sa_column=SQLEnum(StepSystem))
    machine_time: float = Field(default=0.0)
    engineer_time: float = Field(default=0.0)
    date_completed: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    completed: bool = Field(default=False)

    # Relationships
    engineer_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL")
    engineer: User | None = Relationship(back_populates="assigned_step_processes", sa_relationship_kwargs={"foreign_keys": "[StepProcess.engineer_id]"})
    runsheet_id: uuid.UUID = Field(foreign_key="runsheet.id", nullable=False, ondelete="CASCADE")
    runsheet: Runsheet | None = Relationship(back_populates="step_processes")
    samples: list["Sample"] = Relationship(
        back_populates="step_processes",
        link_model=SampleStepProcessLink,
        sa_relationship_kwargs={
            "primaryjoin": "StepProcess.id==SampleStepProcessLink.step_process_id",
            "secondaryjoin": "Sample.id==SampleStepProcessLink.sample_id",
            "foreign_keys": "[SampleStepProcessLink.step_process_id, SampleStepProcessLink.sample_id]"
        }
    )

    # Creation relationship
    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    creator: User | None = Relationship(back_populates="created_step_processes", sa_relationship_kwargs={"foreign_keys": "[StepProcess.creator_id]"})

    # String representation
    def __repr__(self) -> str:
        return f"<StepProcess id={self.id} step_number={self.step_number} title={self.title} completed={self.completed}>"
