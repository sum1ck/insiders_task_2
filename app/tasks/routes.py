# routes.py for tasks feature 
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from tasks.schemas import TaskCreate, TaskUpdate, TaskRead, TaskList
from tasks.service import TaskService
from core.database import get_async_session

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_async_session)
):
    return await TaskService.create_task(db, task_in)


@router.get("/", response_model=TaskList)
async def list_tasks(
    status: Optional[str] = Query(None, description="completed|pending"),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    tasks, total = await TaskService.get_tasks(db, skip=skip, limit=limit, status=status)
    return TaskList(total=total, items=tasks)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    task = await TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    task = await TaskService.update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    success = await TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


@router.post("/{task_id}/complete", response_model=TaskRead)
async def mark_task_completed(
    task_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    task = await TaskService.mark_task_completed(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 