import uuid

from sqlmodel import Session

from app. crud.runsheet import create_runsheet
from app.enums.material import Material
from app.models import StepProcess
from app.schemas.runsheet import RunsheetCreate
from app.schemas.user import UserUpdate
from tests.utils.utils import random_email, random_lower_string


def create_basic_step_process(db: Session, creator_id: uuid.UUID, runsheet_id: uuid.UUID) -> StepProcess:
    # TODO: Change this to depend from CRUD
    step_process = StepProcess(
        runsheet_id=runsheet_id,
        creator_id=creator_id,
        step_number=1,
        title="Step Process Test",
        details="Step process 1",
    )
    db.add(step_process)
    db.commit()
    db.refresh(step_process)
    return step_process
