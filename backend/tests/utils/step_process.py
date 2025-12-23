import uuid

from sqlmodel import Session

from app.crud.step_process import create_step_process
from app.models import StepProcess
from app.schemas.step_process import StepProcessCreate


def create_basic_step_process(db: Session, creator_id: uuid.UUID, runsheet_id: uuid.UUID, step_number: int | None) -> StepProcess:
    step_process_in = StepProcessCreate(
        title="Step Process for Test",
        details="Basic Step Process",
    )
    step_process = create_step_process(
        db=db,
        step_process_in=step_process_in,
        creator_id=creator_id,
        runsheet_id=runsheet_id,
        step_number=step_number,
    )
    return step_process
