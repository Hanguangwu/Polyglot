from datetime import datetime, timedelta
from bson import ObjectId
from typing import List, Optional
from app.core.database import words
from app.models.word import WordCreate, WordUpdate

def get_words_by_user(user_id: str) -> List[dict]:
    """获取用户的所有单词"""
    cursor = words.find({"user_id": user_id}).sort("created_at", -1)
    result = []
    for word in cursor:
        word["id"] = str(word.pop("_id"))
        result.append(word)
    return result

def get_word_by_id(word_id: str, user_id: str) -> Optional[dict]:
    """根据ID获取单词"""
    word = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if word:
        word["id"] = str(word.pop("_id"))
    return word

def create_word(word: WordCreate, user_id: str) -> dict:
    """创建新单词"""
    word_dict = word.model_dump()
    word_dict["user_id"] = user_id
    word_dict["created_at"] = datetime.utcnow()
    word_dict["last_review"] = None
    word_dict["next_review"] = datetime.utcnow()  # 设置为当前时间，使其可以立即复习
    word_dict["review_count"] = 0
    word_dict["difficulty"] = "medium"  # 默认难度为中等
    
    result = words.insert_one(word_dict)
    created = words.find_one({"_id": result.inserted_id})
    created["id"] = str(created.pop("_id"))
    
    return created

def update_word(word_id: str, word_update: WordUpdate, user_id: str) -> Optional[dict]:
    """更新单词"""
    word = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word:
        return None
    
    update_data = {k: v for k, v in word_update.model_dump().items() if v is not None}
    
    if update_data:
        words.update_one({"_id": ObjectId(word_id)}, {"$set": update_data})
        
    updated = words.find_one({"_id": ObjectId(word_id)})
    updated["id"] = str(updated.pop("_id"))
    
    return updated

def delete_word(word_id: str, user_id: str) -> bool:
    """删除单词"""
    result = words.delete_one({"_id": ObjectId(word_id), "user_id": user_id})
    return result.deleted_count > 0

def get_words_for_review(user_id: str) -> List[dict]:
    """获取需要复习的单词"""
    # 获取当前时间之前应该复习的单词
    now = datetime.utcnow()
    cursor = words.find({
        "user_id": user_id,
        "next_review": {"$lte": now}
    }).sort("next_review", 1)
    
    result = []
    for word in cursor:
        word["id"] = str(word.pop("_id"))
        result.append(word)
    
    return result

def update_word_review_status(word_id: str, difficulty: str, user_id: str) -> Optional[dict]:
    """更新单词复习状态"""
    word = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word:
        return None
    
    # 根据艾宾浩斯遗忘曲线计算下次复习时间
    now = datetime.utcnow()
    review_count = word.get("review_count", 0) + 1
    
    # 根据难度和复习次数调整间隔
    if difficulty == "easy":
        interval_days = [1, 3, 7, 14, 30, 60, 120][min(review_count - 1, 6)]
    elif difficulty == "medium":
        interval_days = [1, 2, 5, 10, 20, 40, 80][min(review_count - 1, 6)]
    else:  # difficult
        interval_days = [1, 1, 3, 7, 14, 30, 60][min(review_count - 1, 6)]
    
    next_review = now + timedelta(days=interval_days)
    
    # 更新单词
    update_data = {
        "last_review": now,
        "next_review": next_review,
        "review_count": review_count,
        "difficulty": difficulty
    }
    
    words.update_one({"_id": ObjectId(word_id)}, {"$set": update_data})
    
    updated = words.find_one({"_id": ObjectId(word_id)})
    updated["id"] = str(updated.pop("_id"))
    
    return updated