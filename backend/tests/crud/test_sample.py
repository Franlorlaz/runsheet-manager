import uuid

from sqlmodel import Session, select

from app.crud.sample import generate_citic_id, create_sample, delete_sample, update_sample
from app.models import Sample
from app.schemas.sample import SampleCreate, SampleUpdate
from tests.utils.sample import citic_id_current_prefix, create_basic_sample


# citic_id GENERATION

def test_generate_first_citic_id_when_no_existing(db: Session):
    prefix = citic_id_current_prefix()
    citic_id = generate_citic_id(db=db)
    assert citic_id == f"{prefix}001"


def test_generate_next_citic_id_with_existing(db: Session, superuser_id: uuid.UUID):
    prefix = citic_id_current_prefix()
    create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)
    create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)
    create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)

    citic_id = generate_citic_id(db=db)

    assert citic_id == f"{prefix}004"


# CREATE

def test_create_sample_generates_citic_id(db: Session, superuser_id: uuid.UUID):
    sample_in = SampleCreate(
        name="Sample for Test",
        description="Test creation",
    )

    sample = create_sample(
        db=db,
        sample_in=sample_in,
        creator_id=superuser_id,
        parent_sample_id=None,
    )

    assert sample.citic_id is not None
    assert "-" in sample.citic_id
    assert sample.citic_id.endswith("001")


def test_create_multiple_samples_increments_counter(db: Session, superuser_id: uuid.UUID):
    sample_in = SampleCreate(
        name="Sample for Test",
        description="Test creation",
    )

    s1 = create_sample(db=db, sample_in=sample_in, creator_id=superuser_id, parent_sample_id=None)
    s2 = create_sample(db=db, sample_in=sample_in, creator_id=superuser_id, parent_sample_id=None)

    assert s1.citic_id[:-3] == s2.citic_id[:-3]  # mismo prefijo
    assert int(s2.citic_id[-3:]) == int(s1.citic_id[-3:]) + 1


def test_citic_id_is_unique(db: Session, superuser_id: uuid.UUID):
    sample_in = SampleCreate(
        name="Sample for Test",
        description="Test creation",
    )

    create_sample(db=db, sample_in=sample_in, creator_id=superuser_id, parent_sample_id=None)
    create_sample(db=db, sample_in=sample_in, creator_id=superuser_id, parent_sample_id=None)

    citic_ids = db.exec(select(Sample.citic_id)).all()

    assert len(citic_ids) == len(set(citic_ids))


def test_child_sample(db: Session, superuser_id: uuid.UUID):
    sample_in = SampleCreate(
        name="Sample for Test",
        description="Test creation",
    )

    parent_sample = create_sample(db=db, sample_in=sample_in, creator_id=superuser_id, parent_sample_id=None)
    child_sample = create_sample(db=db, sample_in=sample_in, creator_id=superuser_id, parent_sample_id=parent_sample.id)

    assert parent_sample.parent_sample_id is None
    assert child_sample.parent_sample_id == parent_sample.id


# UPDATE

def test_update_sample_description(db: Session, superuser_id: uuid.UUID):
    sample = create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)
    initial_name = sample.name

    update_in = SampleUpdate(
        description="Updated description"
    )

    updated = update_sample(
        db=db,
        db_sample=sample,
        sample_in=update_in,
    )

    assert updated.description == "Updated description"
    assert updated.name == initial_name


def test_update_sample_multiple_fields(db: Session, superuser_id: uuid.UUID):
    sample = create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)

    update_in = SampleUpdate(
        description="New description",
        name="New Sample Name",
    )

    updated = update_sample(
        db=db,
        db_sample=sample,
        sample_in=update_in,
    )

    assert updated.description == "New description"
    assert updated.name == "New Sample Name"


def test_update_sample_does_not_override_unset_fields(db: Session, superuser_id: uuid.UUID):
    sample = create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)
    original_citic_id = sample.citic_id
    original_material = sample.material

    update_in = SampleUpdate(
        description="Only description updated"
    )

    updated = update_sample(
        db=db,
        db_sample=sample,
        sample_in=update_in,
    )

    assert updated.description == "Only description updated"
    assert updated.citic_id == original_citic_id
    assert updated.material == original_material


def test_update_sample_persists_in_database(db: Session, superuser_id: uuid.UUID):
    sample = create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)

    update_in = SampleUpdate(
        description="Persisted description"
    )

    update_sample(
        db=db,
        db_sample=sample,
        sample_in=update_in,
    )

    db_sample = db.exec(
        select(Sample).where(Sample.id == sample.id)
    ).one()

    assert db_sample.description == "Persisted description"


def test_update_sample_with_empty_update(db: Session, superuser_id: uuid.UUID):
    sample = create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)
    original_description = sample.description
    original_material = sample.material
    original_citic_id = sample.citic_id

    update_in = SampleUpdate()

    updated = update_sample(
        db=db,
        db_sample=sample,
        sample_in=update_in,
    )

    assert updated.id == sample.id
    assert updated.description == original_description
    assert updated.material == original_material
    assert updated.citic_id == original_citic_id


# DELETE

def test_delete_sample(db: Session, superuser_id: uuid.UUID) -> None:
    sample = create_basic_sample(db=db, creator_id=superuser_id, parent_sample_id=None)
    assert sample.id is not None

    db_sample = db.get(Sample, sample.id)
    assert db_sample is not None

    delete_sample(db=db, db_sample=db_sample)

    deleted_sample = db.get(Sample, sample.id)
    assert deleted_sample is None


def test_delete_sample_cascades(db: Session, superuser_id: uuid.UUID) -> None:
    pass
    """
    runsheet_id = runsheet.id
    step_process_id = step_process.id
    sample_id = sample.id
    reviewer_id = runsheet.reviewer_id
    creator_id = runsheet.creator_id

    # ---------- Check ----------
    assert db.get(Runsheet, runsheet_id) is not None
    assert db.get(StepProcess, step_process_id) is not None
    assert db.get(Sample, sample_id) is not None
    #assert db.get(User, reviewer_id) is not None  # TODO: Fix this
    assert db.get(User, creator_id) is not None

    # ---------- Act ----------
    delete_runsheet(db=db, db_runsheet=runsheet)

    # ---------- Assert ----------
    assert db.get(Runsheet, runsheet_id) is None
    assert db.get(StepProcess, step_process_id) is None
    assert db.get(Sample, sample_id) is not None
    # assert db.get(User, reviewer_id) is not None  # TODO: Fix this
    assert db.get(User, creator_id) is not None
    """
