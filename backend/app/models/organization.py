from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class MemberRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    sales_rep = "sales_rep"
    support_rep = "support_rep"
    readonly = "readonly"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    members = relationship("OrganizationMember", back_populates="organization")
    leads = relationship("Lead", back_populates="organization")
    deals = relationship("Deal", back_populates="organization")
    tasks = relationship("Task", back_populates="organization")
    workflows = relationship("Workflow", back_populates="organization")


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(SAEnum(MemberRole), default=MemberRole.sales_rep, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="org_memberships")
