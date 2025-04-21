from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

# 更新 PyObjectId 类以适应 Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if not ObjectId.is_valid(v):
            raise ValueError("无效的 ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    username: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None

class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id")
    username: Optional[str] = None
    hashed_password: str
    avatar: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(UserBase):
    id: str
    username: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_db_model(cls, db_user: 'UserInDB') -> 'User':
        return cls(
            id=str(db_user.id) if isinstance(db_user.id, ObjectId) else db_user.id,
            email=db_user.email,
            username=db_user.username,
            avatar=db_user.avatar,
            created_at=db_user.created_at
        )

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None