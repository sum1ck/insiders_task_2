from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
import datetime
from pydantic import ConfigDict
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    overdue = "overdue"

class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime.datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    status: Optional[TaskStatus] = None


class TaskRead(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    total: int
    items: List[TaskRead]

    model_config = ConfigDict(from_attributes=True)
