from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class WritingBase(BaseModel):
    title: str
    content: str
    topic: str
    time_spent: Optional[int] = None

class WritingCreate(WritingBase):
    pass

class WritingUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    topic: Optional[str] = None
    time_spent: Optional[int] = None
    
    # 添加新字段用于存储AI反馈
    feedback: Optional[str] = None
    score: Optional[float] = None
    corrected_content: Optional[str] = None
    model_essay: Optional[str] = None

class Writing(WritingBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 添加新字段用于存储AI反馈
    feedback: Optional[str] = None
    score: Optional[float] = None
    corrected_content: Optional[str] = None
    model_essay: Optional[str] = None
    
    class Config:
        from_attributes = True