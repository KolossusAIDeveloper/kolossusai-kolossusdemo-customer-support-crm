from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class WorkflowStepCreate(BaseModel):
    step_order: str
    action_type: str
    action_config: Dict[str, Any] = {}
    requires_approval: bool = False


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Dict[str, Any] = {}
    steps: List[WorkflowStepCreate] = []


class WorkflowOut(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    trigger_type: str
    trigger_config: Dict[str, Any]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
