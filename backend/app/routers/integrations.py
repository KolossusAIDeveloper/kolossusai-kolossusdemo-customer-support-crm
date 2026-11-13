from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.integration import Integration
from app.routers.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("")
def list_integrations(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Integration).filter(Integration.organization_id == org_id).all()


@router.post("")
def create_integration(
    org_id: str,
    provider: str,
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    integ = Integration(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        provider=provider,
        name=name,
        status="connected"
    )
    db.add(integ)
    db.commit()
    db.refresh(integ)
    return integ


@router.post("/{integ_id}/test")
def test_integration(integ_id: str, org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    integ = db.query(Integration).filter(Integration.id == integ_id, Integration.organization_id == org_id).first()
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")
    return {"status": "ok", "message": f"Connection to {integ.provider} tested successfully (mock)"}


@router.delete("/{integ_id}")
def delete_integration(integ_id: str, org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    integ = db.query(Integration).filter(Integration.id == integ_id, Integration.organization_id == org_id).first()
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")
    db.delete(integ)
    db.commit()
    return {"message": "Deleted"}
