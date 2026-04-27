from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.task import TaskStatus


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _validate_future(value: datetime) -> datetime:
    due_date = _as_aware_utc(value)
    if due_date <= datetime.now(timezone.utc):
        raise ValueError("due_date must be in the future")
    return due_date


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    due_date: datetime

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, value: datetime) -> datetime:
        return _validate_future(value)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus | None = None
    due_date: datetime | None = None

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        return _validate_future(value)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    due_date: datetime
    created_at: datetime
    updated_at: datetime


class TaskList(BaseModel):
    total: int
    items: list[TaskRead]
