import uuid

from sqlmodel import Session, select

from app.models import Runsheet, Sample, User
from app.schemas.runsheet.creation import RunsheetCreate
# from app.schemas.runsheet.updating import RunsheetUpdate
from app.enums.runsheet_state import RunsheetState
from app.utils import generate_citic_id_for_runsheet


def create_runsheet(*, session: Session, runsheet_in: RunsheetCreate, creator_id: uuid.UUID) -> Runsheet:
    prefix = generate_citic_id_for_runsheet([], prefix_only=True)
    existing_citic_ids = session.exec(
        select(Runsheet.citic_id).where(Runsheet.citic_id.startswith(prefix))
    ).all()
    citic_id = generate_citic_id_for_runsheet(existing_citic_ids, prefix=prefix)

    auto_update = {
        "creator_id": creator_id,
        "state": RunsheetState.edit,
        "citic_id": citic_id,
    }
    db_runsheet = Runsheet.model_validate(runsheet_in, update=auto_update)
    session.add(db_runsheet)
    session.commit()
    session.refresh(db_runsheet)
    return db_runsheet
