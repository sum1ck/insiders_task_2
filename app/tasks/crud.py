from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from tasks.models import Task, TaskStatus
from tasks.schemas import TaskCreate, TaskUpdate
from typing import Optional, List
import datetime

async def create_task(db: AsyncSession, task_in: TaskCreate) -> Task:
    now = datetime.datetime.now(datetime.timezone.utc)
    status = TaskStatus.pending
    if task_in.due_date and task_in.due_date < now:
        status = TaskStatus.overdue
    task = Task(**task_in.dict(), status=status)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None
) -> (List[Task], int):
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    total = await db.execute(select(func.count()).select_from(query.subquery()))
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all(), total.scalar()


async def update_task(db: AsyncSession, task_id: int, task_in: TaskUpdate) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None
    for field, value in task_in.dict(exclude_unset=True).items():
        setattr(task, field, value)
    now = datetime.datetime.now(datetime.timezone.utc)
    if task.due_date and task.due_date < now and task.status != TaskStatus.completed:
        task.status = TaskStatus.overdue
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return False
    await db.delete(task)
    await db.commit()
    return True


async def mark_task_completed(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    if task.due_date and task.due_date < now:
        return task
    task.status = TaskStatus.completed
    await db.commit()
    await db.refresh(task)
    return task
