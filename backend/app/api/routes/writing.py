from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.user import UserInDB
from app.models.writing import Writing, WritingCreate, WritingUpdate
from app.services.writing import (
    get_writings_by_user, get_writing_by_id, create_writing, 
    update_writing, delete_writing, check_writing
)
from typing import List, Optional

# 确保创建了router实例
router = APIRouter()

# 确保路由路径正确
@router.get("/", response_model=List[Writing])
async def get_writings(current_user: UserInDB = Depends(get_current_user)):
    return get_writings_by_user(str(current_user.id))

@router.get("/{writing_id}", response_model=Writing)
async def get_writing(
    writing_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    writing = get_writing_by_id(writing_id, str(current_user.id))
    if not writing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing not found"
        )
    return writing

@router.post("/", response_model=Writing)
async def create_writing_endpoint(
    writing: WritingCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    return create_writing(writing, str(current_user.id))

@router.put("/{writing_id}", response_model=Writing)
async def update_writing_endpoint(
    writing_id: str,
    writing_update: WritingUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    updated_writing = update_writing(writing_id, writing_update, str(current_user.id))
    if not updated_writing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing not found"
        )
    return updated_writing

@router.delete("/{writing_id}", response_model=bool)
async def delete_writing_endpoint(
    writing_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    success = delete_writing(writing_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing not found"
        )
    return success

@router.post("/check", response_model=dict)
async def check_writing_endpoint(
    data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    if "content" not in data or "topic" not in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content and topic are required"
        )
    
    return check_writing(data["content"], data["topic"])