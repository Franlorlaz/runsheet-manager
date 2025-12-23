import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.models import Sample, User
from app.schemas.sample import SampleCreate, SampleUpdate
from app.utils import upgrade_str_counter


# Utils

def generate_citic_id(*, db: Session) -> str:
    """Generate a unique citic_id for a sample.

    Format of citic_id: YYMMDD-000
        YY - last two digits of the year
        MM - two-digit month number
        DD - two-digit day of the month
        000 - counter starting from 001 for each day

    Example:
        251201-001, 251201-002, 251202-001
    """
    today = datetime.today()
    year = today.strftime("%y")
    month = today.month
    day = today.day
    date_prefix = f"{year}{month:02d}{day:02d}-"

    existing_citic_ids = db.exec(
        select(Sample.citic_id).where(Sample.citic_id.startswith(date_prefix))
    ).all()

    return str(upgrade_str_counter(existing_citic_ids, prefix=date_prefix))


# TODO: Revisa estas funciones + Haz lo Tests

# Basic CRUD

def create_sample(*, db: Session, sample_in: SampleCreate, creator_id: uuid.UUID, parent_sample_id: uuid.UUID | None) -> Sample:
    auto_update = {
        "creator_id": creator_id,
        "citic_id": generate_citic_id(db=db),
        "parent_sample_id": parent_sample_id,
        "supervisors": [db.get(User, creator_id)],
    }
    db_sample = Sample.model_validate(sample_in, update=auto_update)
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def update_sample(*, db: Session, db_sample: Sample, sample_in: SampleUpdate) -> Sample:
    sample_data = sample_in.model_dump(exclude_unset=True)
    db_sample.sqlmodel_update(sample_data)
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def delete_sample(*, db: Session, db_sample: Sample) -> None:
    db.delete(db_sample)
    db.commit()


# TODO: Funciones por hacer + Tests


# Attach Relationships

def attach_supervisors_to_sample() -> Sample:
    pass


# Special Functions

def add_notes_to_sample() -> Sample:
    pass


def destroy_sample() -> Sample:  # Just change "exist" to False.
    pass


def split_sample(n_dices) -> list[Sample]:
    pass


# Readers and Indexers

def get_sample_by_id(citic_id: str | None = None) -> Sample:
    pass


def get_samples(filters, sorters) -> list[Sample]:
    pass
