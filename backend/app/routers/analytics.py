from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStage
from app.models.task import Task, TaskStatus
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    total_leads = db.query(Lead).filter(Lead.organization_id == org_id, Lead.is_deleted == False).count()
    new_leads_week = db.query(Lead).filter(
        Lead.organization_id == org_id,
        Lead.is_deleted == False,
        Lead.created_at >= week_ago
    ).count()
    qualified_leads = db.query(Lead).filter(
        Lead.organization_id == org_id,
        Lead.is_deleted == False,
        Lead.status == LeadStatus.qualified
    ).count()

    total_deals = db.query(Deal).filter(Deal.organization_id == org_id, Deal.is_deleted == False).count()
    won_deals = db.query(Deal).filter(Deal.organization_id == org_id, Deal.stage == DealStage.won).count()
    lost_deals = db.query(Deal).filter(Deal.organization_id == org_id, Deal.stage == DealStage.lost).count()

    pipeline_value_row = db.query(func.sum(Deal.value)).filter(
        Deal.organization_id == org_id,
        Deal.is_deleted == False,
        Deal.stage.notin_([DealStage.won, DealStage.lost])
    ).scalar()
    pipeline_value = float(pipeline_value_row or 0)

    expected_revenue_row = db.query(func.sum(Deal.value * Deal.probability / 100)).filter(
        Deal.organization_id == org_id,
        Deal.is_deleted == False,
        Deal.stage.notin_([DealStage.lost])
    ).scalar()
    expected_revenue = float(expected_revenue_row or 0)

    overdue_tasks = db.query(Task).filter(
        Task.organization_id == org_id,
        Task.is_deleted == False,
        Task.due_date < now,
        Task.status.notin_([TaskStatus.completed, TaskStatus.cancelled])
    ).count()

    conversion_rate = round(won_deals / total_leads * 100, 1) if total_leads > 0 else 0

    return {
        "total_leads": total_leads,
        "new_leads_week": new_leads_week,
        "qualified_leads": qualified_leads,
        "conversion_rate": conversion_rate,
        "pipeline_value": pipeline_value,
        "expected_revenue": expected_revenue,
        "won_deals": won_deals,
        "lost_deals": lost_deals,
        "overdue_tasks": overdue_tasks,
    }


@router.get("/pipeline")
def pipeline_analytics(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stages = {}
    for stage in DealStage:
        deals = db.query(Deal).filter(
            Deal.organization_id == org_id,
            Deal.is_deleted == False,
            Deal.stage == stage
        ).all()
        stages[stage.value] = {
            "count": len(deals),
            "value": sum(d.value for d in deals)
        }
    return stages


@router.get("/lead-scores")
def lead_score_distribution(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leads = db.query(Lead).filter(Lead.organization_id == org_id, Lead.is_deleted == False).all()
    hot = sum(1 for l in leads if l.ai_classification == "hot")
    warm = sum(1 for l in leads if l.ai_classification == "warm")
    cold = sum(1 for l in leads if l.ai_classification == "cold")
    unscored = sum(1 for l in leads if not l.ai_classification)
    return {"hot": hot, "warm": warm, "cold": cold, "unscored": unscored}
