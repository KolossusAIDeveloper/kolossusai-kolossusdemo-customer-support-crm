from sqlalchemy.orm import Session
from app.models.task import Notification
import uuid


def create_notification(db: Session, org_id: str, user_id: str, title: str, message: str = None, type: str = "info"):
    notif = Notification(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=user_id,
        title=title,
        message=message,
        type=type
    )
    db.add(notif)
    db.commit()
    return notif
