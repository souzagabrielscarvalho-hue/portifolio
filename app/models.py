from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class ModelChoice(str, Enum):
    sonnet = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    nova =   "us.amazon.nova-pro-v1:0"
    haiku =  "us.anthropic.claude-3-haiku-20240307-v1:0"

class QueryRequest(SQLModel):
    session_id: str
    message: str
    model_choice: ModelChoice = ModelChoice.sonnet

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    role: str
    content: str
    model_used: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    