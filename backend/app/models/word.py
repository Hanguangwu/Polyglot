from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WordBase(BaseModel):
    name: str  # 改为 name 而不是 word
    trans: List[str] = []  # 改为 trans 而不是 translation
    usphone: Optional[str] = None  # 添加 usphone
    ukphone: Optional[str] = None  # 添加 ukphone
    definition: Optional[str] = None  # 添加 definition
    example: Optional[str] = None
    category: Optional[str] = None

class WordCreate(WordBase):
    pass

class WordUpdate(BaseModel):
    name: Optional[str] = None  # 改为 name
    trans: Optional[List[str]] = None  # 改为 trans
    usphone: Optional[str] = None
    ukphone: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None
    category: Optional[str] = None

# 添加缺失的WordImport类
class WordImport(BaseModel):
    words: List[WordCreate]

class Word(WordBase):
    id: str
    user_id: str
    favorite: bool = False  # 添加 favorite 字段
    learned: bool = False  # 添加 learned 字段
    created_at: datetime
    last_reviewed: Optional[datetime] = None  # 改为 last_reviewed
    review_count: int = 0

    class Config:
        from_attributes = True