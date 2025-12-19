from sqlmodel import Field, SQLModel


# Shared properties
class StepProcessBase(SQLModel):
    title: str = Field(default=None, max_length=255)
