from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.conversation import Conversation, Message, MessageSender
from app.models.audit import AuditLog
from app.schemas.conversation import ConversationCreate, ConversationOut, MessageCreate, MessageOut
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.ai_service import ai_service
import uuid

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut)
def create_conversation(
    data: ConversationCreate,
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = Conversation(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        assigned_user_id=current_user.id,
        **data.model_dump()
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Conversation).filter(Conversation.organization_id == org_id).all()


@router.get("/{conv_id}", response_model=ConversationOut)
def get_conversation(conv_id: str, org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.organization_id == org_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.post("/{conv_id}/messages", response_model=MessageOut)
def add_message(
    conv_id: str,
    org_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.organization_id == org_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv_id,
        sender_name=current_user.full_name,
        **data.model_dump()
    )
    db.add(msg)

    if data.sender_type == MessageSender.agent and msg.is_sent:
        log = AuditLog(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            user_id=current_user.id,
            event_type="message_sent",
            resource_type="message",
            resource_id=msg.id
        )
        db.add(log)

    db.commit()
    db.refresh(msg)
    return msg


@router.post("/{conv_id}/ai-suggest")
async def ai_suggest_reply(
    conv_id: str,
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.organization_id == org_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = [{"sender": m.sender_type, "content": m.content} for m in conv.messages[-10:]]
    suggestion = await ai_service.suggest_reply(str(messages))
    summary = await ai_service.summarize_conversation(messages)

    conv.ai_summary = summary
    db.commit()

    return {
        "suggested_reply": suggestion,
        "summary": summary,
        "ai_label": "AI-generated — requires human approval before sending"
    }


@router.post("/{conv_id}/messages/{msg_id}/approve")
def approve_message(
    conv_id: str,
    msg_id: str,
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = db.query(Message).filter(
        Message.id == msg_id,
        Message.conversation_id == conv_id
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.is_approved = True
    log = AuditLog(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=current_user.id,
        event_type="message_approved",
        resource_type="message",
        resource_id=msg_id
    )
    db.add(log)
    db.commit()
    return {"message": "Approved"}
