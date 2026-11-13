from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class ConversationChannel(str, enum.Enum):
    email = "email"
    chat = "chat"
    form = "form"
    webhook = "webhook"
    internal = "internal"


class MessageSender(str, enum.Enum):
    customer = "customer"
    agent = "agent"
    ai = "ai"
    system = "system"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    assigned_user_id = Column(String, ForeignKey("users.id"), nullable=True)

    subject = Column(String, nullable=True)
    channel = Column(SAEnum(ConversationChannel), default=ConversationChannel.email)
    status = Column(String, default="open")
    sentiment = Column(String, nullable=True)
    ai_summary = Column(Text, nullable=True)
    tags = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    messages = relationship("Message", back_populates="conversation")
    assigned_user = relationship("User")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_type = Column(SAEnum(MessageSender), nullable=False)
    sender_name = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    is_ai_suggested = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
