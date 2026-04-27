from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_async_db
from app.core.exceptions import NotFoundError
from app.crud.task import task_crud
from app.models.task import TaskStatus
from app.schemas.response import Response
from app.schemas.task import TaskCreate, TaskList, TaskRead, TaskUpdate
from app.services.notification_service import NotificationService

router = APIRouter(dependencies=[Depends(deps.require_api_key)])


@router.get("", response_model=Response[TaskList], summary="任务列表")
async def list_tasks(
    db: AsyncSession = Depends(get_async_db),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Any:
    items, total = await task_crud.get_list(
        db,
        status=status_filter,
        skip=offset,
        limit=limit,
    )
    return Response(message="获取成功", data=TaskList(total=total, items=items))


@router.get("/{task_id}", response_model=Response[TaskRead], summary="任务详情")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    task = await task_crud.get(db, id=task_id)
    if task is None:
        raise NotFoundError("任务不存在")
    return Response(message="获取成功", data=task)


@router.post(
    "",
    response_model=Response[TaskRead],
    status_code=status.HTTP_201_CREATED,
    summary="创建任务",
)
async def create_task(
    *,
    db: AsyncSession = Depends(get_async_db),
    task_in: TaskCreate,
) -> Any:
    task = await task_crud.create(db, obj_in=task_in)
    return Response(code=201, message="创建成功", data=task)


@router.put("/{task_id}", response_model=Response[TaskRead], summary="更新任务")
async def update_task(
    *,
    task_id: int,
    task_in: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    task = await task_crud.get(db, id=task_id)
    if task is None:
        raise NotFoundError("任务不存在")

    was_completed = task.status == TaskStatus.COMPLETED
    updated_task = await task_crud.update(db, db_obj=task, obj_in=task_in)
    is_newly_completed = (
        not was_completed and updated_task.status == TaskStatus.COMPLETED
    )

    if is_newly_completed:
        background_tasks.add_task(
            NotificationService().send_task_completed_email,
            updated_task.id,
            updated_task.title,
            updated_task.description,
            updated_task.due_date,
        )

    return Response(message="更新成功", data=updated_task)


@router.delete("/{task_id}", response_model=Response[None], summary="删除任务")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    task = await task_crud.get(db, id=task_id)
    if task is None:
        raise NotFoundError("任务不存在")

    await task_crud.delete(db, id=task_id)
    return Response(message="删除成功")
