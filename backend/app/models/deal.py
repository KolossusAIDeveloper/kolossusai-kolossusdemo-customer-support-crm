from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class DealStage(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    demo_scheduled = "demo_scheduled"
    proposal_sent = "proposal_sent"
    negotiation = "negotiation"
    won = "won"
    lost = "lost"


class Deal(Base):
    __tablename__ = "deals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    assigned_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)

    name = Column(String, nullable=False)
    company = Column(String, nullable=True)
    primary_contact = Column(String, nullable=True)
    value = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    probability = Column(Integer, default=50)
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    stage = Column(SAEnum(DealStage), default=DealStage.new, nullable=False, index=True)
    products = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    lost_reason = Column(String, nullable=True)

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", back_populates="deals")
    assigned_user = relationship("User")
