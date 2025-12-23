from sqlmodel import Field, SQLModel

from app.enums.material import Material


# Shared properties
class RunsheetBase(SQLModel):
    material: Material | None = Field(default=None)
    description: str | None = Field(default=None, max_length=1024)


# Properties to receive via API on creation
class RunsheetCreate(RunsheetBase):
    pass


# Properties to receive via API on update
class RunsheetUpdate(RunsheetBase):
    pass
