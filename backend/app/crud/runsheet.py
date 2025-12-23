import uuid
from calendar import month_abbr
from datetime import datetime

from sqlmodel import Session, select

from app.enums.runsheet_state import RunsheetState
from app.models import Runsheet
from app.schemas.runsheet import RunsheetCreate, RunsheetUpdate
from app.utils import upgrade_str_counter


# Utils

def generate_citic_id(*, db: Session) -> str:
    """Generate a unique citic_id for a runsheet.

    Format of citic_id: YYmmm-000
        YY - last two digits of the year
        mmm - three-letter month abbreviation in lowercase
        000 - counter starting from 001 for each month

    Example:
        25dic-001, 25dic-002, 25feb-001
    """
    today = datetime.today()
    year = today.strftime("%y")
    month = month_abbr[today.month].lower()
    date_prefix = f"{year}{month}-"

    existing_citic_ids = db.exec(
        select(Runsheet.citic_id).where(Runsheet.citic_id.startswith(date_prefix))
    ).all()

    return str(upgrade_str_counter(existing_citic_ids, prefix=date_prefix))


# Basic CRUD

def create_runsheet(*, db: Session, runsheet_in: RunsheetCreate, creator_id: uuid.UUID) -> Runsheet:
    auto_update = {
        "creator_id": creator_id,
        "state": RunsheetState.edit,
        "citic_id": generate_citic_id(db=db),
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


# TODO: Funciones por hacer + Tests


# Attach Relationships

def attach_reviewer_to_runsheet() -> Runsheet:
    pass


def attach_set_processes_to_runsheet() -> Runsheet:
    pass


def attach_samples_to_runsheet() -> Runsheet:
    pass


# Special Functions

def upgrade_runsheet_state() -> Runsheet:
    pass



# Readers and Indexers

def get_runsheet_by_id(citic_id: str | None = None) -> Runsheet:
    pass


def get_runsheets(filters, sorters) -> list[Runsheet]:
    pass
