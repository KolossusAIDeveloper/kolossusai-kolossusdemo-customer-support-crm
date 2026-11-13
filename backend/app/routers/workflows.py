from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workflow import Workflow, WorkflowStep, WorkflowExecution
from app.schemas.workflow import WorkflowCreate, WorkflowOut
from app.routers.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowOut)
def create_workflow(
    data: WorkflowCreate,
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wf = Workflow(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        created_by_id=current_user.id,
        name=data.name,
        description=data.description,
        trigger_type=data.trigger_type,
        trigger_config=data.trigger_config
    )
    db.add(wf)
    db.flush()
    for step in data.steps:
        s = WorkflowStep(id=str(uuid.uuid4()), workflow_id=wf.id, **step.model_dump())
        db.add(s)
    db.commit()
    db.refresh(wf)
    return wf


@router.get("", response_model=list[WorkflowOut])
def list_workflows(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Workflow).filter(Workflow.organization_id == org_id).all()


@router.patch("/{wf_id}/toggle")
def toggle_workflow(wf_id: str, org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == wf_id, Workflow.organization_id == org_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.is_active = not wf.is_active
    db.commit()
    return {"is_active": wf.is_active}


@router.get("/{wf_id}/executions")
def list_executions(wf_id: str, org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WorkflowExecution).filter(
        WorkflowExecution.workflow_id == wf_id,
        WorkflowExecution.organization_id == org_id
    ).order_by(WorkflowExecution.started_at.desc()).limit(20).all()
