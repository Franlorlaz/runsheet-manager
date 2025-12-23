import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.api.deps import get_db
from app.core.config import settings
from app.core.db import engine, init_db
from app.core.security import get_password_hash
from app.crud.runsheet import create_runsheet
from app.crud.user import get_user_by_email
from app.enums.material import Material
from app.main import app
from app.models import Item, Runsheet, Sample, StepProcess, User
from app.schemas.runsheet.creation import RunsheetCreate
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    with Session(engine) as session:
        init_db(session)

        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()

        if not user:
            user = User(
                email=settings.FIRST_SUPERUSER,
                hashed_password=get_password_hash(
                    settings.FIRST_SUPERUSER_PASSWORD
                ),
                is_active=True,
                is_superuser=True,
            )
            session.add(user)
            session.commit()


@pytest.fixture(scope="function", autouse=True)
def override_get_db(db: Session):
    def _get_db_override():
        yield db

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="function")
def superuser_id(db: Session) -> uuid.UUID:
    user = get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    return user.id
