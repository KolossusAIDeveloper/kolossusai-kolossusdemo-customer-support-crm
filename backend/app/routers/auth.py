from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization, OrganizationMember, MemberRole
from app.models.audit import AuditLog
from app.schemas.auth import UserRegister, Token, UserOut, OrgOut
from app.services.auth_service import (
    get_password_hash, authenticate_user, create_access_token, decode_token, get_user_by_email
)
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def get_current_org_member(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrganizationMember:
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    return member


@router.post("/register", response_model=Token)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        is_verified=True
    )
    db.add(user)
    db.flush()

    if data.org_name:
        slug = data.org_name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
        org = Organization(id=str(uuid.uuid4()), name=data.org_name, slug=slug)
        db.add(org)
        db.flush()
        member = OrganizationMember(
            id=str(uuid.uuid4()),
            organization_id=org.id,
            user_id=user.id,
            role=MemberRole.owner
        )
        db.add(member)

    log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user.id,
        event_type="user_registered",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email}
    )
    db.add(log)
    db.commit()

    # Get user's first org
    member = db.query(OrganizationMember).filter(OrganizationMember.user_id == user.id).first()
    org_id = member.organization_id if member else None

    token = create_access_token({"sub": user.id})
    return Token(access_token=token, org_id=org_id)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user.id,
        event_type="user_login",
        resource_type="user",
        resource_id=user.id
    )
    db.add(log)
    db.commit()

    member = db.query(OrganizationMember).filter(OrganizationMember.user_id == user.id).first()
    org_id = member.organization_id if member else None

    token = create_access_token({"sub": user.id})
    return Token(access_token=token, org_id=org_id)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/organizations", response_model=list[OrgOut])
def my_organizations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id
    ).all()
    return [m.organization for m in memberships]
