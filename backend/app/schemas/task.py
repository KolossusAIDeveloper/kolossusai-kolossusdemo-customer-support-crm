from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    lead_id: Optional[str] = None
    deal_id: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    assigned_user_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_user_id: Optional[str] = None


class TaskOut(BaseModel):
    id: str
    organization_id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    lead_id: Optional[str]
    deal_id: Optional[str]
    assigned_user_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
