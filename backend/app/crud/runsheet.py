import uuid

from sqlmodel import Session, select

from app.enums.runsheet_state import RunsheetState
from app.models import Runsheet
from app.schemas.runsheet.creation import RunsheetCreate
from app.schemas.runsheet.updating import RunsheetUpdate
from app.utils import generate_citic_id_for_runsheet


def create_runsheet(*, db: Session, runsheet_in: RunsheetCreate, creator_id: uuid.UUID) -> Runsheet:
    prefix = generate_citic_id_for_runsheet([], prefix_only=True)
    existing_citic_ids = db.exec(
        select(Runsheet.citic_id).where(Runsheet.citic_id.startswith(prefix))
    ).all()
    citic_id = generate_citic_id_for_runsheet(existing_citic_ids, prefix=prefix)

    auto_update = {
        "creator_id": creator_id,
        "state": RunsheetState.edit,
        "citic_id": citic_id,
    }
    db_runsheet = Runsheet.model_validate(runsheet_in, update=auto_update)
    db.add(db_runsheet)
    db.commit()
    db.refresh(db_runsheet)
    return db_runsheet


def update_runsheet(*, db: Session, db_runsheet: Runsheet, runsheet_in: RunsheetUpdate) -> Runsheet:
    runsheet_data = runsheet_in.model_dump(exclude_unset=True)
    db_runsheet.sqlmodel_update(runsheet_data)
    db.add(db_runsheet)
    db.commit()
    db.refresh(db_runsheet)
    return db_runsheet


def delete_runsheet(*, db: Session, db_runsheet: Runsheet) -> None:
    db.delete(db_runsheet)
    db.commit()
