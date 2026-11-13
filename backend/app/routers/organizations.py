from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.organization import Organization, OrganizationMember, MemberRole
from app.models.user import User
from app.models.audit import AuditLog
from app.routers.auth import get_current_user
from app.services.auth_service import get_user_by_email
import uuid

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.get("/{org_id}/members")
def list_members(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    members = db.query(OrganizationMember).filter(OrganizationMember.organization_id == org_id).all()
    return [{"id": m.id, "user_id": m.user_id, "role": m.role, "email": m.user.email, "name": m.user.full_name} for m in members]


@router.post("/{org_id}/invite")
def invite_member(
    org_id: str,
    email: str,
    role: MemberRole = MemberRole.sales_rep,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found — they must register first")
    existing = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already a member")
    member = OrganizationMember(id=str(uuid.uuid4()), organization_id=org_id, user_id=user.id, role=role)
    db.add(member)
    log = AuditLog(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=current_user.id,
        event_type="member_invited",
        details={"email": email, "role": role}
    )
    db.add(log)
    db.commit()
    return {"message": f"Invited {email} as {role}"}
