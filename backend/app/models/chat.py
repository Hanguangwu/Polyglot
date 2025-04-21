from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str
    audio_url: Optional[str] = None
    corrected_content: Optional[str] = None

class ChatSessionBase(BaseModel):
    title: str
    type: Literal["casual", "ielts"] = "casual"  # 新增类型字段，区分闲聊和雅思口语

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[Message]] = None

class ChatSession(ChatSessionBase):
    id: str
    user_id: str
    created_at: datetime
    messages: List[Message] = []

    class Config:
        from_attributes = True

class AudioTranscriptionResult(BaseModel):
    text: str
    score: Optional[float] = None
    feedback: Optional[str] = None