from sqlmodel import Field, SQLModel


# Shared properties
class RunsheetBase(SQLModel):
    citic_id: str = Field(unique=True, index=True, max_length=255)
