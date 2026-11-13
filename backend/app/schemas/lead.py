from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.lead import LeadStatus, LeadPriority, LeadSource


class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    source: LeadSource = LeadSource.manual
    priority: LeadPriority = LeadPriority.medium
    notes: Optional[str] = None
    next_follow_up: Optional[datetime] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    source: Optional[LeadSource] = None
    notes: Optional[str] = None
    lead_score: Optional[int] = None
    next_follow_up: Optional[datetime] = None
    assigned_user_id: Optional[str] = None


class LeadOut(BaseModel):
    id: str
    organization_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    industry: Optional[str]
    country: Optional[str]
    status: LeadStatus
    priority: LeadPriority
    source: LeadSource
    lead_score: int
    ai_classification: Optional[str]
    ai_reasoning: Optional[str]
    ai_recommended_action: Optional[str]
    notes: Optional[str]
    last_activity: Optional[datetime]
    next_follow_up: Optional[datetime]
    assigned_user_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    items: List[LeadOut]
    total: int
    page: int
    per_page: int
