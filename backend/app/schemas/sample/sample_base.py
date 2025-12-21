from sqlmodel import Field, SQLModel


# Shared properties
class SampleBase(SQLModel):
    citic_id: str = Field(unique=True, index=True, max_length=255)
    name: str | None = Field(default=None, max_length=255)
