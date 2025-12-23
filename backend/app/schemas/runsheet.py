from sqlmodel import Field, SQLModel

from app.enums.material import Material


# Shared properties
class RunsheetBase(SQLModel):
    citic_id: str = Field(unique=True, index=True, max_length=255)


# Properties to receive via API on creation
class RunsheetCreate(SQLModel):
    material: Material = Field(default=Material.other)
    description: str | None = Field(default=None, max_length=1024)


# Properties to receive via API on update
class RunsheetUpdate(SQLModel):
    material: Material | None = Field(default=None)
    description: str | None = Field(default=None, max_length=1024)
