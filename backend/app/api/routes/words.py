from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Response
from typing import List, Optional
from app.models.user import User
from app.api.deps import get_current_user
from app.services.word import (
    get_words_by_user,
    get_favorite_words_by_user,
    get_learned_words_by_user,
    get_review_words_by_user,
    create_word,
    get_word_by_id,
    update_word,
    delete_word,
    toggle_favorite,
    toggle_learned,
    import_words_from_json,
    export_words_to_json,
    update_word_review_status_service  # 添加这个函数导入
)
from app.models.word import WordCreate, Word, WordUpdate, WordImport
import httpx

router = APIRouter()

@router.get("/", response_model=List[Word])
async def get_words(
    current_user: User = Depends(get_current_user),
    limit: Optional[int] = Query(None, description="限制返回的单词数量"),
    random: bool = Query(False, description="是否随机选择单词")
):
    """获取用户的单词列表"""
    return get_words_by_user(str(current_user.id), limit, random)

@router.get("/favorites", response_model=List[Word])
async def get_favorite_words(current_user: User = Depends(get_current_user)):
    return get_favorite_words_by_user(str(current_user.id))

@router.get("/learned", response_model=List[Word])
async def get_learned_words(current_user: User = Depends(get_current_user)):
    return get_learned_words_by_user(str(current_user.id))

@router.get("/review", response_model=List[Word])
async def get_review_words(current_user: User = Depends(get_current_user)):
    return get_review_words_by_user(str(current_user.id))

# 其他路由处理函数也需要修改 UserInDB 为 User
@router.post("/", response_model=Word)
async def add_word(
    word: WordCreate,
    current_user: User = Depends(get_current_user)
):
    return create_word(word, str(current_user.id))

@router.put("/{word_id}", response_model=Word)
async def update_word_endpoint(
    word_id: str,
    word_update: WordUpdate,
    current_user: User = Depends(get_current_user)
):
    updated_word = update_word(word_id, word_update, str(current_user.id))
    if not updated_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return updated_word

@router.delete("/{word_id}", response_model=bool)
async def delete_word_endpoint(
    word_id: str,
    current_user: User = Depends(get_current_user)
):
    success = delete_word(word_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return success

@router.put("/{word_id}/favorite", response_model=Word)
async def toggle_word_favorite(
    word_id: str,
    favorite: bool = Query(..., description="是否收藏"),
    current_user: User = Depends(get_current_user)
):
    updated_word = toggle_favorite(word_id, favorite, str(current_user.id))
    if not updated_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return updated_word

@router.put("/{word_id}/learned", response_model=Word)
async def toggle_word_learned(
    word_id: str,
    learned: bool = Query(..., description="是否已学会"),
    current_user: User = Depends(get_current_user)
):
    updated_word = toggle_learned(word_id, learned, str(current_user.id))
    if not updated_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return updated_word

@router.post("/import", response_model=List[Word])
async def import_words(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 导入单词
        imported_words = import_words_from_json(content_str, str(current_user.id))
        if not imported_words:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid words found in the file"
            )
        
        return imported_words
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding not supported"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/export")
async def export_words(current_user: User = Depends(get_current_user)):
    json_content = export_words_to_json(str(current_user.id))
    
    response = Response(content=json_content)
    response.headers["Content-Disposition"] = f"attachment; filename=words.json"
    response.headers["Content-Type"] = "application/json"
    
    return response

@router.get("/youdao")
async def proxy_youdao(word: str, current_user: User = Depends(get_current_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://dict.youdao.com/suggest?num=1&doctype=json&q={word}",
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Youdao data: {str(e)}"
        )


@router.post("/{word_id}/review", response_model=Word)
async def update_word_review_status(
    word_id: str,
    data: dict,
    current_user: User = Depends(get_current_user)
):
    """更新单词的复习状态"""
    difficulty = data.get("difficulty")
    if not difficulty or difficulty not in ["easy", "medium", "difficult"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid difficulty level"
        )
    
    # 调用服务函数更新复习状态
    updated_word = update_word_review_status_service(word_id, difficulty, str(current_user.id))
    if not updated_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return updated_word