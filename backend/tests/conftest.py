import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.crud.runsheet import create_runsheet
from app.enums.material import Material
from app.main import app
from app.models import Item, Runsheet, Sample, StepProcess, User
from app.schemas.runsheet.creation import RunsheetCreate
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="module")
def superuser_id(db: Session) -> uuid.UUID:
    user = User(
        name="Superuser",
        email=f"superuser_{uuid.uuid4().hex}@test.com",
        is_superuser=True,
        is_active=True,
        is_reviewer=True,
        hashed_password="fake",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


@pytest.fixture(scope="module")
def reviewer_user_id(db: Session) -> uuid.UUID:
    user = User(
        name="Reviewer User",
        email=f"reviewer_user_{uuid.uuid4().hex}@test.com",
        is_superuser=False,
        is_active=True,
        is_reviewer=True,
        hashed_password="fake",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


@pytest.fixture(scope="module")
def basic_user_id(db: Session) -> uuid.UUID:
    user = User(
        name="Basic User",
        email=f"basic_user_{uuid.uuid4().hex}@test.com",
        is_superuser=False,
        is_active=True,
        is_reviewer=False,
        hashed_password="fake",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


@pytest.fixture(scope="module")
def runsheet(db: Session, basic_user_id):
    runsheet_in = RunsheetCreate(
        material=Material.silicon,
        description="Initial description",
    )
    return create_runsheet(
        db=db,
        runsheet_in=runsheet_in,
        creator_id=basic_user_id,
    )


@pytest.fixture(scope="module")
def step_process(db: Session, runsheet, basic_user_id):
    step_process = StepProcess(
        runsheet_id=runsheet.id,
        creator_id=basic_user_id,
        step_number=1,
        title="Step Process Test",
        details="Step process 1",
    )
    db.add(step_process)
    db.commit()
    db.refresh(step_process)
    return step_process


@pytest.fixture(scope="module")
def sample(db: Session, basic_user_id):
    sample = Sample(
        citic_id="251222-001",
        name="Sample A",
        creator_id=basic_user_id,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


@pytest.fixture(scope="module")
def runsheet_with_links(db: Session, runsheet_in, sample, reviewer_user_id):
    runsheet = db.get(Runsheet, runsheet_in.id)
    runsheet.reviewer_id = reviewer_user_id
    runsheet.samples.append(sample)
    db.add(runsheet)
    db.commit()
    db.refresh(runsheet)
    return runsheet
