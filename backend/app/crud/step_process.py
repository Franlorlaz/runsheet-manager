import uuid

from sqlmodel import Session, select

from app.models import StepProcess, User
# from app.schemas.step_process.creation import StepProcessCreate
# from app.schemas.step_process.updating import StepProcessUpdate


# TODO: Funciones por hacer + Tests

# Basic CRUD

def create_step_process() -> StepProcess:
    pass


def update_step_process() -> StepProcess:
    pass


def delete_step_process() -> None:
    pass


# Attach Relationships

def attach_samples_to_step_process() -> StepProcess:
    pass


# Special Functions

def add_notes_to_step_process() -> StepProcess:
    pass


def complete_step_process(samples) -> StepProcess:
    pass


def reorder_step_processes() -> list[StepProcess]:
    pass


# Readers and Indexers

def get_step_process_by_id() -> StepProcess:
    pass


def get_step_processes(filters, sorters) -> list[StepProcess]:
    pass
