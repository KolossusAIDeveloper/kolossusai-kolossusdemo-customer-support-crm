from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    unqualified = "unqualified"
    converted = "converted"
    lost = "lost"


class LeadPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class LeadSource(str, enum.Enum):
    manual = "manual"
    csv_import = "csv_import"
    web_form = "web_form"
    webhook = "webhook"
    email = "email"
    website = "website"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    assigned_user_id = Column(String, ForeignKey("users.id"), nullable=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True, index=True)
    company = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)

    status = Column(SAEnum(LeadStatus), default=LeadStatus.new, nullable=False, index=True)
    priority = Column(SAEnum(LeadPriority), default=LeadPriority.medium, nullable=False)
    source = Column(SAEnum(LeadSource), default=LeadSource.manual, nullable=False)

    lead_score = Column(Integer, default=0)
    ai_classification = Column(String, nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    ai_recommended_action = Column(String, nullable=True)

    notes = Column(Text, nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    next_follow_up = Column(DateTime(timezone=True), nullable=True)

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", back_populates="leads")
    assigned_user = relationship("User")
    ai_recommendations = relationship("AIRecommendation", back_populates="lead")
