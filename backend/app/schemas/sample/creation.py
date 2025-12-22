import uuid

from sqlmodel import Field, SQLModel

from app.enums.material import Material
from app.enums.sample_type import SampleType


# Properties to receive via API on creation
class SampleCreate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2048)
    location: str | None = Field(default=None, max_length=255)
    type: SampleType | None = Field(default=SampleType.other)
    material: Material | None = Field(default=Material.other)
    parent_sample_id: uuid.UUID | None = Field(default=None)
