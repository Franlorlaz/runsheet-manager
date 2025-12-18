import uuid

from sqlmodel import Field, Relationship, SQLModel

from app.schemas.user import UserBase
from app.schemas.user.user_creation import UserCreate, UserRegister
from app.schemas.user.user_updating import UserUpdate, UserUpdateMe, UpdatePassword
from app.schemas.user.user_returns import UserPublic, UsersPublic

from app.schemas.item import ItemBase
from app.schemas.item.item_creation import ItemCreate
from app.schemas.item.item_updating import ItemUpdate
from app.schemas.item.item_returns import ItemPublic, ItemsPublic

from app.schemas.general import Message, Token, TokenPayload, NewPassword


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")
