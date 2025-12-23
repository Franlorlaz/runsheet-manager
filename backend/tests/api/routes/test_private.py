from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import User
from tests.utils.utils import random_email


def test_create_user(client: TestClient, db: Session) -> None:
    rand_email = random_email()
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": rand_email,
            "password": "password123",
            "name": "Pollo Listo",
        },
    )

    assert r.status_code == 200

    data = r.json()

    user = db.exec(select(User).where(User.id == data["id"])).first()

    assert user
    assert user.email == rand_email
    assert user.name == "Pollo Listo"
