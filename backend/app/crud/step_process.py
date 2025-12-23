import uuid

from sqlmodel import Session, select

from app.models import StepProcess, User
from app.schemas.step_process.creation import StepProcessCreate
from app.schemas.step_process.updating import StepProcessUpdate
from app.utils import upgrade_str_counter


# TODO: Funciones por hacer + Tests

# Basic CRUD

def create_step_process(*, db: Session, step_process_in: StepProcessCreate, creator_id: uuid.UUID, runsheet_id: uuid.UUID | None, step_number: int | None = None) -> StepProcess:
    if not step_number:
        existing_step_numbers: list[str] = [
            str(n)
            for n in db.exec(select(StepProcess.step_number).where(StepProcess.runsheet_id == runsheet_id)).all()
        ]
        step_number = int(upgrade_str_counter(existing_step_numbers))
    auto_update = {
        "step_number": step_number,
        "runsheet_id": runsheet_id,
        "creator_id": creator_id,
    }
    db_step_process = StepProcess.model_validate(step_process_in, update=auto_update)
    db.add(db_step_process)
    db.commit()
    db.refresh(db_step_process)
    return db_step_process


def update_step_process(*, db: Session, db_step_process: StepProcess, step_process_in: StepProcessUpdate) -> StepProcess:
    setp_data = step_process_in.model_dump(exclude_unset=True)
    db_step_process.sqlmodel_update(setp_data)
    db.add(db_step_process)
    db.commit()
    db.refresh(db_step_process)
    return db_step_process


def delete_step_process(*, db: Session, db_step_process: StepProcess) -> None:
    db.delete(db_step_process)
    db.commit()


# Attach Relationships

def attach_samples_to_step_process() -> StepProcess:
    pass


# Special Functions

def add_notes_to_step_process() -> StepProcess:
    pass


def complete_step_process(samples) -> StepProcess:
    pass


def reorder_step_processes() -> list[StepProcess]:
    pass


# Readers and Indexers

def get_step_process_by_id() -> StepProcess:
    pass


def get_step_processes(filters, sorters) -> list[StepProcess]:
    pass
