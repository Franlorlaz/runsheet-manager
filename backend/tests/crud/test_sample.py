import uuid

from sqlmodel import Session

from app.crud.sample import generate_citic_id
from tests.utils.sample import citic_id_current_prefix


# citic_id GENERATION

def test_generate_first_citic_id_when_no_existing(db: Session):
    prefix = citic_id_current_prefix()
    citic_id = generate_citic_id(db=db)
    assert citic_id == f"{prefix}001"


def test_generate_next_citic_id_with_existing(db: Session, superuser_id: uuid.UUID):
    pass
    """
    prefix = citic_id_current_prefix()
    create_basic_runsheet(db=db, creator_id=superuser_id)
    create_basic_runsheet(db=db, creator_id=superuser_id)
    create_basic_runsheet(db=db, creator_id=superuser_id)

    citic_id = generate_citic_id(db=db)

    assert citic_id == f"{prefix}004"
    """
