from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.deal import DealStage


class DealCreate(BaseModel):
    name: str
    company: Optional[str] = None
    primary_contact: Optional[str] = None
    value: float = 0.0
    currency: str = "USD"
    probability: int = 50
    expected_close_date: Optional[datetime] = None
    stage: DealStage = DealStage.new
    lead_id: Optional[str] = None
    products: Optional[str] = None
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    primary_contact: Optional[str] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    stage: Optional[DealStage] = None
    products: Optional[str] = None
    notes: Optional[str] = None
    lost_reason: Optional[str] = None
    assigned_user_id: Optional[str] = None


class DealMoveStage(BaseModel):
    stage: DealStage
    lost_reason: Optional[str] = None


class DealOut(BaseModel):
    id: str
    organization_id: str
    name: str
    company: Optional[str]
    primary_contact: Optional[str]
    value: float
    currency: str
    probability: int
    expected_close_date: Optional[datetime]
    stage: DealStage
    lead_id: Optional[str]
    products: Optional[str]
    notes: Optional[str]
    lost_reason: Optional[str]
    assigned_user_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DealListResponse(BaseModel):
    items: List[DealOut]
    total: int
    page: int
    per_page: int
