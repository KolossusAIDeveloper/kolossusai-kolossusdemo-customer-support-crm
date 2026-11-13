from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.conversation import ConversationChannel, MessageSender


class ConversationCreate(BaseModel):
    subject: Optional[str] = None
    channel: ConversationChannel = ConversationChannel.email
    lead_id: Optional[str] = None


class MessageCreate(BaseModel):
    content: str
    sender_type: MessageSender = MessageSender.agent
    sender_name: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    sender_type: MessageSender
    sender_name: Optional[str]
    content: str
    is_ai_suggested: bool
    is_approved: bool
    is_sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: str
    organization_id: str
    subject: Optional[str]
    channel: ConversationChannel
    status: str
    sentiment: Optional[str]
    ai_summary: Optional[str]
    lead_id: Optional[str]
    assigned_user_id: Optional[str]
    created_at: datetime
    messages: List[MessageOut] = []

    model_config = {"from_attributes": True}
