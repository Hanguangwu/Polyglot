from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.core.security import get_current_user
from app.models.user import UserInDB
from app.models.chat import ChatSession, ChatSessionCreate, ChatSessionUpdate, Message
from app.services.chat import (
    get_chat_sessions_by_user, get_chat_session_by_id, create_chat_session, 
    update_chat_session, delete_chat_session, add_message_to_session, 
    get_ai_response, process_audio
)
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[ChatSession])
async def get_chat_sessions(current_user: UserInDB = Depends(get_current_user)):
    return get_chat_sessions_by_user(str(current_user.id))

@router.get("/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    session = get_chat_session_by_id(session_id, str(current_user.id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return session

@router.post("/", response_model=ChatSession)
async def create_chat_session_endpoint(
    session: ChatSessionCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    return create_chat_session(session, str(current_user.id))

@router.put("/{session_id}", response_model=ChatSession)
async def update_chat_session_endpoint(
    session_id: str,
    session_update: ChatSessionUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    updated_session = update_chat_session(session_id, session_update, str(current_user.id))
    if not updated_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return updated_session

@router.delete("/{session_id}", response_model=bool)
async def delete_chat_session_endpoint(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    success = delete_chat_session(session_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return success

@router.post("/{session_id}/messages", response_model=ChatSession)
async def add_message(
    session_id: str,
    message: Message,
    current_user: UserInDB = Depends(get_current_user)
):
    return add_message_to_session(session_id, message, str(current_user.id))

@router.post("/{session_id}/ai-response", response_model=dict)
async def get_ai_response_endpoint(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    return get_ai_response(session_id, str(current_user.id))

@router.post("/{session_id}/upload-audio", response_model=dict)
async def upload_audio(
    session_id: str,
    audio_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    return process_audio(audio_file, session_id, str(current_user.id))