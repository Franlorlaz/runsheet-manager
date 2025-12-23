import uuid
from datetime import datetime
from calendar import month_abbr

from sqlmodel import Session

from app.crud.sample import create_sample
from app.enums.material import Material
from app.models import Sample
from app.schemas.sample import SampleCreate
from app.schemas.user import UserUpdate
from tests.utils.utils import random_email, random_lower_string


def citic_id_current_prefix() -> str:
    today = datetime.today()
    year = today.strftime("%y")
    month = today.month
    day = today.day
    return f"{year}{month:02d}{day:02d}-"


def create_basic_sample(db: Session, creator_id: uuid.UUID, parent_sample_id: uuid.UUID | None) -> Sample:
    sample_in = SampleCreate(
        name="Sample for Test",
        description="Basic Sample Generator",
    )
    sample = create_sample(
        db=db,
        sample_in=sample_in,
        creator_id=creator_id,
        parent_sample_id=parent_sample_id,
    )
    return sample
