import uuid
from datetime import datetime

from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import UUID
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


# Basic CRUD

def create_sample(*, db: Session, sample_in: SampleCreate, creator_id: uuid.UUID, parent_sample_id: uuid.UUID | None) -> Sample:
    sample_data = sample_in.model_dump(exclude_unset=True)

    creator = db.get(User, creator_id)
    if not creator:
        raise Exception("create_sample() - creator_id does not exist in DB")
    
    parent_sample = db.get(Sample, parent_sample_id)
    if parent_sample_id and not parent_sample:
        raise Exception("create_sample() - parent_sample_id does not exist in DB")
    
    auto_update = {
        "creator_id": creator_id,
        "citic_id": generate_citic_id(db=db),
        "parent_sample_id": parent_sample_id,
        "supervisors": [db.get(User, creator_id)],
    }
    db_sample = Sample.model_validate(sample_data, update=auto_update)
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

def attach_supervisors_to_sample(*, db: Session, db_sample: Sample, supervisor_ids: list[uuid.UUID]) -> Sample:
    if not supervisor_ids:
        return db_sample

    # Obtener usuarios válidos
    supervisors = db.exec(
        select(User).where(cast(User.id, UUID).in_(supervisor_ids))
    ).all()

    if not supervisors:
        return db_sample

    # Evitar duplicados
    existing_ids = {user.id for user in db_sample.supervisors}

    for supervisor in supervisors:
        if supervisor.id not in existing_ids:
            db_sample.supervisors.append(supervisor)

    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)

    return db_sample


def replace_supervisors_of_sample(*, db: Session, db_sample: Sample, supervisor_ids: list[uuid.UUID]) -> Sample:
    supervisors = db.exec(
        select(User).where(cast(User.id, UUID).in_(supervisor_ids))
    ).all()

    db_sample.supervisors = list(supervisors)

    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)

    return db_sample


def detach_supervisors_from_sample(*, db: Session, db_sample: Sample, supervisor_ids: list[uuid.UUID]) -> Sample:
    if not supervisor_ids:
        return db_sample

    # Filtrar supervisores actualmente asociados que deban eliminarse
    supervisors_to_remove = [
        supervisor
        for supervisor in db_sample.supervisors
        if supervisor.id in supervisor_ids
    ]

    for supervisor in supervisors_to_remove:
        db_sample.supervisors.remove(supervisor)

    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)

    return db_sample


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
