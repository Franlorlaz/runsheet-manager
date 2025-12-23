import uuid

from sqlmodel import Session, select

from app.crud.step_process import create_step_process, delete_step_process, update_step_process
from app.models import StepProcess
from app.schemas.step_process import StepProcessCreate, StepProcessUpdate
from tests.utils.runsheet import create_basic_runsheet
from tests.utils.step_process import create_basic_step_process


# CREATE

def test_step_process_belongs_to_a_runsheet(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process_in = StepProcessCreate(
        title="Step Process for Test",
        details="Test creation",
    )

    step_process = create_step_process(
        db=db,
        step_process_in=step_process_in,
        creator_id=superuser_id,
        runsheet_id=runsheet.id,
        step_number=None,
    )

    assert step_process.runsheet_id == runsheet.id


def test_create_first_step_process_generates_first_step_number(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process_in = StepProcessCreate(
        title="Step Process for Test",
        details="Test creation",
    )

    step_process = create_step_process(
        db=db,
        step_process_in=step_process_in,
        creator_id=superuser_id,
        runsheet_id=runsheet.id,
        step_number=None,
    )

    assert step_process.step_number == 1


def test_create_multiple_step_process_increments_counter(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process_in = StepProcessCreate(
        title="Step Process for Test",
        details="Test creation",
    )

    s1 = create_step_process(db=db, step_process_in=step_process_in, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)
    s2 = create_step_process(db=db, step_process_in=step_process_in, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)

    assert s1.step_number == 1
    assert s2.step_number == 2


def test_step_number_is_unique(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process_in = StepProcessCreate(
        title="Step Process for Test",
        details="Test creation",
    )

    create_step_process(db=db, step_process_in=step_process_in, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)
    create_step_process(db=db, step_process_in=step_process_in, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)

    step_numbers = db.exec(select(StepProcess.step_number).where(StepProcess.runsheet_id == runsheet.id)).all()

    assert len(step_numbers) == len(set(step_numbers))


# UPDATE

def test_update_step_process_details(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process = create_basic_step_process(db=db, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)
    initial_title = step_process.title

    update_in = StepProcessUpdate(
        details="Updated details"
    )

    updated = update_step_process(
        db=db,
        db_step_process=step_process,
        step_process_in=update_in,
    )

    assert updated.details == "Updated details"
    assert updated.title == initial_title


def test_update_step_process_multiple_fields(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process = create_basic_step_process(db=db, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)

    update_in = StepProcessUpdate(
        details="New details",
        title="New Title",
    )

    updated = update_step_process(
        db=db,
        db_step_process=step_process,
        step_process_in=update_in,
    )

    assert updated.details == "New details"
    assert updated.title == "New Title"


def test_update_step_process_does_not_override_unset_fields(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process = create_basic_step_process(db=db, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)
    original_step_number = step_process.step_number
    original_title = step_process.title

    update_in = StepProcessUpdate(
        details="Only details updated"
    )

    updated = update_step_process(
        db=db,
        db_step_process=step_process,
        step_process_in=update_in,
    )

    assert updated.details == "Only details updated"
    assert updated.step_number == original_step_number
    assert updated.title == original_title


def test_update_step_process_persists_in_database(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process = create_basic_step_process(db=db, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)

    update_in = StepProcessUpdate(
        details="Persisted details"
    )

    update_step_process(
        db=db,
        db_step_process=step_process,
        step_process_in=update_in,
    )

    db_step_process = db.exec(
        select(StepProcess).where(StepProcess.id == step_process.id)
    ).one()

    assert db_step_process.details == "Persisted details"


def test_update_step_process_with_empty_update(db: Session, superuser_id: uuid.UUID):
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process = create_basic_step_process(db=db, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)
    original_details = step_process.details
    original_title = step_process.title
    original_step_number = step_process.step_number

    update_in = StepProcessUpdate()

    updated = update_step_process(
        db=db,
        db_step_process=step_process,
        step_process_in=update_in,
    )

    assert updated.id == step_process.id
    assert updated.details == original_details
    assert updated.title == original_title
    assert updated.step_number == original_step_number


# DELETE

def test_delete_step_process(db: Session, superuser_id: uuid.UUID) -> None:
    runsheet = create_basic_runsheet(db=db, creator_id=superuser_id)
    step_process = create_basic_step_process(db=db, creator_id=superuser_id, runsheet_id=runsheet.id, step_number=None)
    assert step_process.id is not None

    db_step_process = db.get(StepProcess, step_process.id)
    assert db_step_process is not None

    delete_step_process(db=db, db_step_process=db_step_process)

    deleted_step_process = db.get(StepProcess, step_process.id)
    assert deleted_step_process is None


def test_delete_step_process_cascades(db: Session, superuser_id: uuid.UUID) -> None:
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
