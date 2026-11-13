from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.models.lead import Lead
from app.models.audit import AuditLog, AIRecommendation
from app.schemas.lead import LeadCreate, LeadUpdate, LeadOut, LeadListResponse
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.ai_service import ai_service
import uuid
import json

router = APIRouter(prefix="/api/leads", tags=["leads"])


def require_org_lead(lead_id: str, org_id: str, db: Session) -> Lead:
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.organization_id == org_id, Lead.is_deleted == False).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("", response_model=LeadOut)
async def create_lead(
    data: LeadCreate,
    org_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check for duplicates
    if data.email:
        existing = db.query(Lead).filter(
            Lead.organization_id == org_id,
            Lead.email == data.email,
            Lead.is_deleted == False
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Lead with this email already exists")

    lead = Lead(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        assigned_user_id=current_user.id,
        **data.model_dump()
    )
    db.add(lead)

    log = AuditLog(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=current_user.id,
        event_type="lead_created",
        resource_type="lead",
        resource_id=lead.id,
        details={"name": lead.name, "email": lead.email}
    )
    db.add(log)
    db.commit()
    db.refresh(lead)

    background_tasks.add_task(score_lead_background, lead.id, org_id, data.model_dump())
    return lead


async def score_lead_background(lead_id: str, org_id: str, lead_data: dict):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        result = await ai_service.score_lead(lead_data)
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            lead.lead_score = result.get("score", 0)
            lead.ai_classification = result.get("classification")
            lead.ai_reasoning = json.dumps(result.get("reasoning", []))
            lead.ai_recommended_action = result.get("recommended_action")

            rec = AIRecommendation(
                id=str(uuid.uuid4()),
                organization_id=org_id,
                lead_id=lead_id,
                model_name=result.get("model_name", "unknown"),
                prompt_version=result.get("prompt_version", "1.0"),
                score=str(result.get("score", 0)),
                classification=result.get("classification"),
                intent=result.get("intent"),
                reasoning=result.get("reasoning", []),
                recommended_action=result.get("recommended_action"),
                confidence=str(result.get("confidence", 0))
            )
            db.add(rec)
            db.commit()
    finally:
        db.close()


@router.get("", response_model=LeadListResponse)
def list_leads(
    org_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Lead).filter(Lead.organization_id == org_id, Lead.is_deleted == False)

    if search:
        query = query.filter(or_(
            Lead.name.ilike(f"%{search}%"),
            Lead.email.ilike(f"%{search}%"),
            Lead.company.ilike(f"%{search}%")
        ))
    if status:
        query = query.filter(Lead.status == status)
    if priority:
        query = query.filter(Lead.priority == priority)

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return LeadListResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: str,
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return require_org_lead(lead_id, org_id, db)


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: str,
    org_id: str,
    data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lead = require_org_lead(lead_id, org_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    log = AuditLog(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=current_user.id,
        event_type="lead_updated",
        resource_type="lead",
        resource_id=lead.id
    )
    db.add(log)
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
def delete_lead(
    lead_id: str,
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lead = require_org_lead(lead_id, org_id, db)
    lead.is_deleted = True
    log = AuditLog(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=current_user.id,
        event_type="lead_deleted",
        resource_type="lead",
        resource_id=lead.id
    )
    db.add(log)
    db.commit()
    return {"message": "Lead deleted"}
