from sqlmodel import Field, SQLModel

from app.enums.material import Material


# Properties to receive via API on creation
class RunsheetCreate(SQLModel):
    material: Material = Field(default=Material.other)
    description: str | None = Field(default=None, max_length=1024)
