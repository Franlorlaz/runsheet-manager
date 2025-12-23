import uuid
from datetime import datetime
from calendar import month_abbr

from sqlmodel import Session

from app. crud.runsheet import create_runsheet
from app.enums.material import Material
from app.models import Runsheet
from app.schemas.runsheet import RunsheetCreate


def citic_id_current_prefix() -> str:
    today = datetime.today()
    year = today.strftime("%y")
    month = month_abbr[today.month].lower()
    return f"{year}{month}-"


def create_basic_runsheet(db: Session, creator_id: uuid.UUID) -> Runsheet:
    runsheet_in = RunsheetCreate(
        material=Material.other,
        description="Basic Runsheet description",
    )
    return create_runsheet(
        db=db,
        runsheet_in=runsheet_in,
        creator_id=creator_id,
    )


def create_runsheet_with_relationships(db: Session, runsheet_in, sample, reviewer_user_id) -> Runsheet:
    pass
    """
    runsheet = db.get(Runsheet, runsheet_in.id)
    runsheet.reviewer_id = reviewer_user_id
    runsheet.samples.append(sample)
    db.add(runsheet)
    db.commit()
    db.refresh(runsheet)
    return runsheet
    """
