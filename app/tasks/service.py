from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tasks import crud
from tasks.schemas import TaskCreate, TaskUpdate
from typing import Optional, List
import datetime
from core.celery_app import celery_app
from tasks.models import Task, TaskStatus
from core.config import settings
from sqlalchemy import select
import asyncio
from sqlalchemy import create_engine

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class TaskService:
    @staticmethod
    async def create_task(db: AsyncSession, task_in: TaskCreate) -> Task:
        return await crud.create_task(db, task_in)

    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
        return await crud.get_task(db, task_id)

    @staticmethod
    async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 10, status: Optional[str] = None):
        return await crud.get_tasks(db, skip, limit, status)

    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, task_in: TaskUpdate) -> Optional[Task]:
        return await crud.update_task(db, task_id, task_in)

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> bool:
        return await crud.delete_task(db, task_id)

    @staticmethod
    async def mark_task_completed(db: AsyncSession, task_id: int) -> Optional[Task]:
        return await crud.mark_task_completed(db, task_id)

@celery_app.task(name="tasks.service.mark_overdue_tasks")
def mark_overdue_tasks():
    with SessionLocal() as session:
        now = datetime.datetime.now(datetime.timezone.utc)
        tasks = session.query(Task).filter(
            Task.status == TaskStatus.pending,
            Task.due_date != None,
            Task.due_date < now
        ).all()
        for task in tasks:
            task.status = TaskStatus.overdue
        session.commit() 