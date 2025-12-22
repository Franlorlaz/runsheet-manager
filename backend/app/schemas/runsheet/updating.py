from sqlmodel import Field, SQLModel

from app.enums.material import Material


# Properties to receive via API on creation
class RunsheetUpdate(SQLModel):
    material: Material | None = Field(default=None)
    description: str | None = Field(default=None, max_length=1024)
