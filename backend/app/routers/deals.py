from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.deal import Deal, DealStage
from app.models.audit import AuditLog
from app.schemas.deal import DealCreate, DealUpdate, DealOut, DealListResponse, DealMoveStage
from app.routers.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/deals", tags=["deals"])


def require_org_deal(deal_id: str, org_id: str, db: Session) -> Deal:
    deal = db.query(Deal).filter(Deal.id == deal_id, Deal.organization_id == org_id, Deal.is_deleted == False).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.post("", response_model=DealOut)
def create_deal(
    data: DealCreate,
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deal = Deal(id=str(uuid.uuid4()), organization_id=org_id, assigned_user_id=current_user.id, **data.model_dump())
    db.add(deal)
    log = AuditLog(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=current_user.id,
        event_type="deal_created",
        resource_type="deal",
        resource_id=deal.id,
        details={"name": deal.name}
    )
    db.add(log)
    db.commit()
    db.refresh(deal)
    return deal


@router.get("", response_model=DealListResponse)
def list_deals(
    org_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    stage: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Deal).filter(Deal.organization_id == org_id, Deal.is_deleted == False)
    if stage:
        query = query.filter(Deal.stage == stage)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return DealListResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/{deal_id}", response_model=DealOut)
def get_deal(deal_id: str, org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return require_org_deal(deal_id, org_id, db)


@router.patch("/{deal_id}", response_model=DealOut)
def update_deal(
    deal_id: str,
    org_id: str,
    data: DealUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deal = require_org_deal(deal_id, org_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(deal, field, value)
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/{deal_id}/move-stage", response_model=DealOut)
def move_stage(
    deal_id: str,
    org_id: str,
    data: DealMoveStage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deal = require_org_deal(deal_id, org_id, db)
    old_stage = deal.stage
    deal.stage = data.stage
    if data.lost_reason:
        deal.lost_reason = data.lost_reason
    log = AuditLog(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=current_user.id,
        event_type="deal_stage_changed",
        resource_type="deal",
        resource_id=deal.id,
        details={"from": old_stage, "to": data.stage}
    )
    db.add(log)
    db.commit()
    db.refresh(deal)
    return deal


@router.delete("/{deal_id}")
def delete_deal(deal_id: str, org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deal = require_org_deal(deal_id, org_id, db)
    deal.is_deleted = True
    db.commit()
    return {"message": "Deal deleted"}
