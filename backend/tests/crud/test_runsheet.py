import uuid
from datetime import datetime
from calendar import month_abbr

from sqlmodel import Session, select

from app.crud.runsheet import create_runsheet, update_runsheet, delete_runsheet
from app.enums.material import Material
from app.models import Runsheet, Sample, StepProcess, User
from app.schemas.runsheet.creation import RunsheetCreate
from app.schemas.runsheet.updating import RunsheetUpdate
from app.utils import generate_citic_id_for_runsheet


# citic_id GENERATION

def _current_prefix() -> str:
    today = datetime.today()
    year = today.strftime("%y")
    month = month_abbr[today.month].lower()
    return f"{year}{month}-"


def test_generate_prefix_only():
    prefix = generate_citic_id_for_runsheet([], prefix_only=True)

    assert prefix.endswith("-")
    assert len(prefix) == 6  # YYmmm-


def test_generate_first_citic_id_when_no_existing():
    prefix = _current_prefix()
    citic_id = generate_citic_id_for_runsheet([], prefix=prefix)

    assert citic_id == f"{prefix}001"


def test_generate_next_citic_id_with_existing():
    prefix = _current_prefix()
    existing = [
        f"{prefix}001",
        f"{prefix}002",
        f"{prefix}010",
    ]

    citic_id = generate_citic_id_for_runsheet(existing, prefix=prefix)

    assert citic_id == f"{prefix}011"


def test_ignores_other_months():
    prefix = _current_prefix()
    existing = [
        "24nov-099",
        f"{prefix}003",
        "25jan-001",
    ]

    citic_id = generate_citic_id_for_runsheet(existing, prefix=prefix)

    assert citic_id == f"{prefix}004"


def test_ignores_malformed_citic_ids():
    prefix = _current_prefix()
    existing = [
        f"{prefix}001",
        f"{prefix}abc",
        f"{prefix}",
        "invalid",
    ]

    citic_id = generate_citic_id_for_runsheet(existing, prefix=prefix)

    assert citic_id == f"{prefix}002"


# CREATE Runsheet

def test_create_runsheet_generates_citic_id(db: Session, basic_user_id: uuid.UUID):
    runsheet_in = RunsheetCreate(
        material=Material.other,
        description="Test runsheet",
    )

    runsheet = create_runsheet(
        db=db,
        runsheet_in=runsheet_in,
        creator_id=basic_user_id,
    )

    assert runsheet.citic_id is not None
    assert "-" in runsheet.citic_id
    assert runsheet.citic_id.endswith("001")


def test_create_multiple_runsheets_increments_counter(db: Session, basic_user_id: uuid.UUID):
    runsheet_in = RunsheetCreate(
        material=Material.other,
        description="Test runsheet",
    )

    r1 = create_runsheet(db=db, runsheet_in=runsheet_in, creator_id=basic_user_id)
    r2 = create_runsheet(db=db, runsheet_in=runsheet_in, creator_id=basic_user_id)

    assert r1.citic_id[:-3] == r2.citic_id[:-3]  # mismo prefijo
    assert int(r2.citic_id[-3:]) == int(r1.citic_id[-3:]) + 1


def test_citic_id_is_unique(db: Session, basic_user_id: uuid.UUID):
    runsheet_in = RunsheetCreate(
        material=Material.other,
        description="Test runsheet",
    )

    create_runsheet(db=db, runsheet_in=runsheet_in, creator_id=basic_user_id)
    create_runsheet(db=db, runsheet_in=runsheet_in, creator_id=basic_user_id)

    citic_ids = db.exec(select(Runsheet.citic_id)).all()

    assert len(citic_ids) == len(set(citic_ids))


# UPDATE runsheet

def test_update_runsheet_description(db: Session, runsheet: Runsheet):
    initial_material = runsheet.material
    update_in = RunsheetUpdate(
        description="Updated description"
    )

    updated = update_runsheet(
        db=db,
        db_runsheet=runsheet,
        runsheet_in=update_in,
    )

    assert updated.description == "Updated description"
    assert updated.material == initial_material


def test_update_runsheet_multiple_fields(db: Session, runsheet: Runsheet):
    update_in = RunsheetUpdate(
        description="New description",
        material=Material.graphene,
    )

    updated = update_runsheet(
        db=db,
        db_runsheet=runsheet,
        runsheet_in=update_in,
    )

    assert updated.description == "New description"
    assert updated.material == Material.graphene


def test_update_runsheet_does_not_override_unset_fields(db: Session, runsheet: Runsheet):
    original_citic_id = runsheet.citic_id
    original_material = runsheet.material

    update_in = RunsheetUpdate(
        description="Only description updated"
    )

    updated = update_runsheet(
        db=db,
        db_runsheet=runsheet,
        runsheet_in=update_in,
    )

    assert updated.description == "Only description updated"
    assert updated.citic_id == original_citic_id
    assert updated.material == original_material


def test_update_runsheet_persists_in_database(db: Session, runsheet: Runsheet):
    update_in = RunsheetUpdate(
        description="Persisted description"
    )

    update_runsheet(
        db=db,
        db_runsheet=runsheet,
        runsheet_in=update_in,
    )

    db_runsheet = db.exec(
        select(Runsheet).where(Runsheet.id == runsheet.id)
    ).one()

    assert db_runsheet.description == "Persisted description"


def test_update_runsheet_with_empty_update(db: Session, runsheet: Runsheet):
    original_description = runsheet.description
    original_material = runsheet.material
    original_citic_id = runsheet.citic_id

    update_in = RunsheetUpdate()

    updated = update_runsheet(
        db=db,
        db_runsheet=runsheet,
        runsheet_in=update_in,
    )

    assert updated.id == runsheet.id
    assert updated.description == original_description
    assert updated.material == original_material
    assert updated.citic_id == original_citic_id


# DELETE runsheet


def test_delete_runsheet(db: Session, superuser_id: uuid.UUID) -> None:
    # Arrange: crear runsheet
    runsheet_in = RunsheetCreate(
        material=Material.other,
        description="Runsheet to be deleted",
    )

    runsheet = create_runsheet(
        db=db,
        runsheet_in=runsheet_in,
        creator_id=superuser_id,
    )

    assert runsheet.id is not None

    # Pre-check: existe en BD
    db_runsheet = db.get(Runsheet, runsheet.id)
    assert db_runsheet is not None

    # Act: borrar
    delete_runsheet(db=db, db_runsheet=db_runsheet)

    # Assert: ya no existe
    deleted_runsheet = db.get(Runsheet, runsheet.id)
    assert deleted_runsheet is None


def test_delete_runsheet_cascades_only_step_processes(db: Session, runsheet: Runsheet, step_process: StepProcess, sample: Sample) -> None:
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
