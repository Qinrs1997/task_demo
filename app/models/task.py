from datetime import datetime
import enum

from sqlalchemy import DateTime, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class Task(BaseModel):
    """Task table."""

    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_status_due_date", "status", "due_date"),
        {"comment": "任务表"},
    )

    title: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
        comment="任务标题",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="任务描述",
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True,
        comment="任务状态",
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="截止时间",
    )
