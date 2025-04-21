from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from app.core.database import users
from app.core.security import get_password_hash, verify_password
from app.models.user import UserCreate, UserInDB, User, UserUpdate

def get_user_by_email(email: str) -> UserInDB:
    user_dict = users.find_one({"email": email})
    if user_dict:
        # 确保 _id 字段存在并且是 ObjectId 类型
        if "_id" in user_dict and isinstance(user_dict["_id"], ObjectId):
            # 将 _id 转换为字符串以便 Pydantic 模型处理
            user_dict["id"] = str(user_dict["_id"])
        return UserInDB(**user_dict)
    return None

def get_user_by_id(user_id: str) -> UserInDB:
    try:
        object_id = ObjectId(user_id)
        user_dict = users.find_one({"_id": object_id})
        if user_dict:
            # 确保 _id 字段正确处理
            user_dict["_id"] = object_id
            return UserInDB(**user_dict)
    except Exception as e:
        print(f"获取用户时出错: {e}")
    return None

def authenticate_user(email: str, password: str) -> UserInDB:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(user: UserCreate) -> User:
    # 检查邮箱是否已存在
    if get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建用户文档
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "username": user.username or user.email.split("@")[0],
        "avatar": None,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
    
    # 插入到数据库
    result = users.insert_one(user_data)
    
    # 获取新创建的用户
    created_user = get_user_by_id(str(result.inserted_id))
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # 转换为 User 模型返回
    return User(
        id=str(created_user.id),
        email=created_user.email,
        username=created_user.username,
        avatar=created_user.avatar,
        created_at=created_user.created_at
    )

def update_user(user_id: str, user_update: UserUpdate) -> User:
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    if not update_data:
        return User(
            id=user.id,
            email=user.email,
            username=user.username,
            avatar=user.avatar,
            created_at=user.created_at
        )
    
    # 更新数据库
    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    # 返回更新后的用户信息
    updated_user = get_user_by_id(user_id)
    return User(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        avatar=updated_user.avatar,
        created_at=updated_user.created_at
    )

def change_password(user_id: str, old_password: str, new_password: str) -> bool:
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 验证旧密码
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # 更新密码
    hashed_password = get_password_hash(new_password)
    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    return True