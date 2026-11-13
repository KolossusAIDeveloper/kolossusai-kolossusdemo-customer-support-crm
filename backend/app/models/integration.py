from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    provider = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    config = Column(JSON, default={})
    status = Column(String, default="disconnected")
    last_sync = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
