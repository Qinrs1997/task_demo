from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def get_list(
        self,
        db: AsyncSession,
        *,
        status: TaskStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Task], int]:
        filters = []
        if status is not None:
            filters.append(Task.status == status)

        count_query = select(func.count()).select_from(Task).where(*filters)
        query = (
            select(Task)
            .where(*filters)
            .order_by(Task.id.desc())
            .offset(skip)
            .limit(limit)
        )

        total = await db.scalar(count_query) or 0
        result = await db.execute(query)
        return list(result.scalars().all()), total


task_crud = CRUDTask(Task)
