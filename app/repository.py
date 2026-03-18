from sqlmodel import Session, select
from models import ChatMessage

class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_message(self, session_id: str, role: str, content: str, model_used: str):
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            model_used=model_used
        )
        self.session.add(msg)
        self.session.commit()
        self.session.refresh(msg)
        return msg

    def get_history(self, session_id: str):
        statement = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp)
        return self.session.exec(statement).all()