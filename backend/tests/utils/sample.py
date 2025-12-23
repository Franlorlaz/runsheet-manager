import uuid
from datetime import datetime
from calendar import month_abbr

from sqlmodel import Session

from app. crud.runsheet import create_runsheet
from app.enums.material import Material
from app.models import Sample
from app.schemas.sample import SampleCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


def citic_id_current_prefix() -> str:
    today = datetime.today()
    year = today.strftime("%y")
    month = today.month
    day = today.day
    return f"{year}{month:02d}{day:02d}-"


def create_basic_ssample(db: Session, creator_id: uuid.UUID) -> Sample:
    # TODO: Change this to depend from CRUD
    sample = Sample(
        citic_id="251222-001",
        name="Sample A",
        creator_id=creator_id,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample
