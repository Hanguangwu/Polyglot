from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import json
import random
from fastapi import HTTPException, status, UploadFile
from app.core.database import words
from app.models.word import WordCreate, Word, WordUpdate, WordImport
from datetime import datetime, timedelta

# 修改 get_words_by_user 函数，确保它接受 limit 和 random 参数
def get_words_by_user(user_id: str, limit: Optional[int] = None, random_select: bool = False) -> List[Word]:
    query = {"user_id": user_id}
    
    # 获取所有符合条件的单词
    cursor = words.find(query)
    
    # 如果需要随机选择
    if random_select and limit:
        # 获取总数
        total = words.count_documents(query)
        # 如果总数小于等于限制数，直接返回所有
        if total <= limit:
            word_list = []
            for word_dict in cursor:
                # 转换 ObjectId 为字符串
                word_dict["id"] = str(word_dict.pop("_id"))
                if isinstance(word_dict["user_id"], ObjectId):
                    word_dict["user_id"] = str(word_dict["user_id"])
                word_list.append(Word(**word_dict))
            return word_list
        
        # 随机选择指定数量的单词
        random_indices = random.sample(range(total), limit)
        all_words = list(cursor)
        selected_words = [all_words[i] for i in random_indices if i < len(all_words)]
        
        word_list = []
        for word_dict in selected_words:
            # 转换 ObjectId 为字符串
            word_dict["id"] = str(word_dict.pop("_id"))
            if isinstance(word_dict["user_id"], ObjectId):
                word_dict["user_id"] = str(word_dict["user_id"])
            word_list.append(Word(**word_dict))
        return word_list
    
    # 如果只需要限制数量
    if limit:
        cursor = cursor.limit(limit)
    
    word_list = []
    for word_dict in cursor:
        # 转换 ObjectId 为字符串
        word_dict["id"] = str(word_dict.pop("_id"))
        if isinstance(word_dict["user_id"], ObjectId):
            word_dict["user_id"] = str(word_dict["user_id"])
        word_list.append(Word(**word_dict))
    return word_list

def get_favorite_words_by_user(user_id: str) -> List[Word]:
    query = {"user_id": user_id, "favorite": True}
    cursor = words.find(query)
    
    word_list = []
    for word_dict in cursor:
        # 转换 ObjectId 为字符串
        word_dict["id"] = str(word_dict.pop("_id"))
        if isinstance(word_dict["user_id"], ObjectId):
            word_dict["user_id"] = str(word_dict["user_id"])
        word_list.append(Word(**word_dict))
    return word_list

def get_learned_words_by_user(user_id: str) -> List[Word]:
    query = {"user_id": user_id, "learned": True}
    cursor = words.find(query)
    
    word_list = []
    for word_dict in cursor:
        word_dict["id"] = str(word_dict.pop("_id"))
        if isinstance(word_dict["user_id"], ObjectId):
            word_dict["user_id"] = str(word_dict["user_id"])
        word_list.append(Word(**word_dict))
    return word_list

def create_word(word: WordCreate, user_id: str) -> Word:
    # 检查单词是否已存在
    existing = words.find_one({"name": word.name.lower(), "user_id": user_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word already exists"
        )
    
    # 创建单词文档
    word_dict = word.model_dump()
    word_dict["name"] = word_dict["name"].lower()  # 转换为小写
    word_dict["user_id"] = user_id
    word_dict["favorite"] = False
    word_dict["learned"] = False
    word_dict["created_at"] = datetime.utcnow()
    word_dict["last_reviewed"] = None
    word_dict["review_count"] = 0
    
    # 确保 trans 字段是列表
    if "trans" not in word_dict or word_dict["trans"] is None:
        word_dict["trans"] = []
    
    try:
        # 插入数据库
        result = words.insert_one(word_dict)
        
        # 返回创建的单词
        created_word = words.find_one({"_id": result.inserted_id})
        if not created_word:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create word"
            )
            
        # 确保所有必需字段都存在
        word_data = {
            "id": str(created_word.pop("_id")),
            "name": created_word["name"],
            "user_id": str(created_word["user_id"]) if isinstance(created_word["user_id"], ObjectId) else created_word["user_id"],
            "trans": created_word.get("trans", []),
            "usphone": created_word.get("usphone", ""),
            "ukphone": created_word.get("ukphone", ""),
            "definition": created_word.get("definition", ""),
            "example": created_word.get("example", ""),
            "favorite": created_word.get("favorite", False),
            "learned": created_word.get("learned", False),
            "created_at": created_word.get("created_at", datetime.utcnow()),
            "last_reviewed": created_word.get("last_reviewed"),
            "review_count": created_word.get("review_count", 0)
        }
        
        return Word(**word_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def import_words_from_json(content: str, user_id: str) -> List[Word]:
    try:
        # 解析 JSON 内容
        data = json.loads(content)
        
        # 处理两种可能的格式：直接的单词列表或包含 words 字段的对象
        word_list = data if isinstance(data, list) else data.get("words", [])
        
        imported_words = []
        for word_data in word_list:
            try:
                # 检查必需字段
                if "name" not in word_data:
                    continue
                
                # 检查单词是否已存在
                existing = words.find_one({"name": word_data["name"].lower(), "user_id": user_id})
                if existing:
                    continue
                    
                # 准备单词数据
                word_dict = {
                    "name": word_data["name"].lower(),
                    "trans": word_data.get("trans", []),
                    "usphone": word_data.get("usphone", ""),
                    "ukphone": word_data.get("ukphone", ""),
                    "definition": word_data.get("definition", ""),
                    "example": word_data.get("example", ""),
                    "user_id": user_id,
                    "favorite": False,
                    "learned": False,
                    "created_at": datetime.utcnow(),
                    "last_reviewed": None,
                    "review_count": 0
                }
                
                # 插入数据库
                result = words.insert_one(word_dict)
                
                # 获取插入的单词
                inserted = words.find_one({"_id": result.inserted_id})
                if not inserted:
                    continue
                
                # 准备返回数据
                word_data = {
                    "id": str(inserted.pop("_id")),
                    "name": inserted["name"],
                    "user_id": str(inserted["user_id"]) if isinstance(inserted["user_id"], ObjectId) else inserted["user_id"],
                    "trans": inserted.get("trans", []),
                    "usphone": inserted.get("usphone", ""),
                    "ukphone": inserted.get("ukphone", ""),
                    "definition": inserted.get("definition", ""),
                    "example": inserted.get("example", ""),
                    "favorite": inserted.get("favorite", False),
                    "learned": inserted.get("learned", False),
                    "created_at": inserted.get("created_at", datetime.utcnow()),
                    "last_reviewed": inserted.get("last_reviewed"),
                    "review_count": inserted.get("review_count", 0)
                }
                
                imported_words.append(Word(**word_data))
                
            except Exception as e:
                print(f"Error importing word: {str(e)}")
                continue
                
        return imported_words
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import error: {str(e)}"
        )

# 修复 toggle_favorite 函数
def toggle_favorite(word_id: str, favorite: bool, user_id: str) -> Optional[Word]:
    # 获取单词
    word_dict = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word_dict:
        return None
    
    # 更新收藏状态
    words.update_one(
        {"_id": ObjectId(word_id)},
        {"$set": {"favorite": favorite}}
    )
    
    # 获取更新后的单词
    updated_word = words.find_one({"_id": ObjectId(word_id)})
    if not updated_word:
        return None
    
    # 转换 ObjectId 为字符串
    updated_word["id"] = str(updated_word.pop("_id"))
    if isinstance(updated_word["user_id"], ObjectId):
        updated_word["user_id"] = str(updated_word["user_id"])
    
    return Word(**updated_word)

# 同样修复 toggle_learned 函数
def toggle_learned(word_id: str, learned: bool, user_id: str) -> Optional[Word]:
    # 获取单词
    word_dict = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word_dict:
        return None
    
    # 更新学习状态
    words.update_one(
        {"_id": ObjectId(word_id)},
        {"$set": {"learned": learned}}
    )
    
    # 获取更新后的单词
    updated_word = words.find_one({"_id": ObjectId(word_id)})
    if not updated_word:
        return None
    
    # 转换 ObjectId 为字符串
    updated_word["id"] = str(updated_word.pop("_id"))
    if isinstance(updated_word["user_id"], ObjectId):
        updated_word["user_id"] = str(updated_word["user_id"])
    
    return Word(**updated_word)

# 修复 get_word_by_id 函数
def get_word_by_id(word_id: str, user_id: str) -> Optional[Word]:
    word_dict = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word_dict:
        return None
    
    # 转换 ObjectId 为字符串
    word_dict["id"] = str(word_dict.pop("_id"))
    if isinstance(word_dict["user_id"], ObjectId):
        word_dict["user_id"] = str(word_dict["user_id"])
    
    return Word(**word_dict)

# Add this function after get_word_by_id function

def update_word(word_id: str, word_update: WordUpdate, user_id: str) -> Optional[Word]:
    """
    Update a word's information
    """
    # Check if word exists and belongs to user
    word_dict = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word_dict:
        return None
    
    # Prepare update data
    update_data = word_update.model_dump(exclude_unset=True)
    
    # Update word
    words.update_one(
        {"_id": ObjectId(word_id)},
        {"$set": update_data}
    )
    
    # Get updated word
    updated_word = words.find_one({"_id": ObjectId(word_id)})
    if not updated_word:
        return None
    
    # Convert ObjectId to string
    updated_word["id"] = str(updated_word.pop("_id"))
    if isinstance(updated_word["user_id"], ObjectId):
        updated_word["user_id"] = str(updated_word["user_id"])
    
    return Word(**updated_word)

# 在 update_word 函数后添加

def delete_word(word_id: str, user_id: str) -> bool:
    """
    删除指定的单词
    """
    # 检查单词是否存在且属于该用户
    word_dict = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word_dict:
        return False
    
    # 删除单词
    result = words.delete_one({"_id": ObjectId(word_id)})
    
    # 返回删除是否成功
    return result.deleted_count > 0

def export_words_to_json(user_id: str) -> str:
    """
    导出用户的所有单词到 JSON 格式
    """
    # 获取用户的所有单词
    cursor = words.find({"user_id": user_id})
    
    # 准备导出数据
    word_list = []
    for word_dict in cursor:
        # 移除 MongoDB 特定的字段并转换 ObjectId
        word_dict.pop("_id")
        if isinstance(word_dict["user_id"], ObjectId):
            word_dict["user_id"] = str(word_dict["user_id"])
        
        # 转换时间格式
        if "created_at" in word_dict:
            word_dict["created_at"] = word_dict["created_at"].isoformat()
        if "last_reviewed" in word_dict and word_dict["last_reviewed"]:
            word_dict["last_reviewed"] = word_dict["last_reviewed"].isoformat()
        
        word_list.append(word_dict)
    
    # 创建导出数据结构
    export_data = {
        "words": word_list,
        "exported_at": datetime.utcnow().isoformat(),
        "total_count": len(word_list)
    }
    
    # 转换为 JSON 字符串
    return json.dumps(export_data, ensure_ascii=False, indent=2)


def get_review_words_by_user(user_id: str) -> List[dict]:
    """获取用户需要复习的单词"""
    # 查询需要复习的单词
    cursor = words.find({"user_id": user_id})
    
    word_list = []
    for word in cursor:
        # 确保字段名称正确
        word_data = {
            "id": str(word.pop("_id")),
            "user_id": word.get("user_id", ""),
            "name": word.get("name", ""),  # 使用正确的字段名 name
            "trans": word.get("trans", []),  # 使用正确的字段名 trans
            "usphone": word.get("usphone", None),
            "ukphone": word.get("ukphone", None),
            "definition": word.get("definition", None),
            "example": word.get("example", None),
            "category": word.get("category", None),
            "favorite": word.get("favorite", False),
            "learned": word.get("learned", False),
            "created_at": word.get("created_at", datetime.utcnow()),
            "last_reviewed": word.get("last_reviewed", None),
            "review_count": word.get("review_count", 0)
        }
        
        word_list.append(Word(**word_data))
    
    return word_list
    """
    获取需要复习的单词列表
    规则：
    1. 已学会的单词
    2. 最后复习时间超过指定时间的单词
    3. 按照复习次数和最后复习时间排序
    """
    # 设置复习时间间隔（例如：24小时）
    review_interval = timedelta(hours=24)
    current_time = datetime.utcnow()
    
    # 构建查询条件
    query = {
        "user_id": user_id,
        "learned": True,
        "$or": [
            {"last_reviewed": None},
            {"last_reviewed": {"$lt": current_time - review_interval}}
        ]
    }
    
    # 获取需要复习的单词，按复习次数升序和最后复习时间升序排序
    cursor = words.find(query).sort([
        ("review_count", 1),
        ("last_reviewed", 1)
    ])
    
    word_list = []
    for word_dict in cursor:
        # 转换 ObjectId 为字符串
        word_dict["id"] = str(word_dict.pop("_id"))
        if isinstance(word_dict["user_id"], ObjectId):
            word_dict["user_id"] = str(word_dict["user_id"])
        
        # 将数据库字段映射到 Word 模型字段
        # 确保与 Words.vue 中使用的格式一致
        word_data = {
            "id": word_dict["id"],
            "user_id": word_dict["user_id"],
            "word": word_dict.get("name", ""),  # name -> word
            "translation": ", ".join(word_dict.get("trans", [])) if isinstance(word_dict.get("trans"), list) else word_dict.get("trans", ""),  # trans -> translation
            "phonetic": word_dict.get("usphone", "") or word_dict.get("ukphone", ""),  # usphone/ukphone -> phonetic
            "example": word_dict.get("example", ""),
            "note": word_dict.get("definition", ""),  # definition -> note
            "category": word_dict.get("category", ""),
            "created_at": word_dict.get("created_at", datetime.utcnow()),
            "last_review": word_dict.get("last_reviewed"),
            "next_review": word_dict.get("next_review", datetime.utcnow()),
            "review_count": word_dict.get("review_count", 0),
            "difficulty": word_dict.get("difficulty", "medium")
        }
        
        word_list.append(Word(**word_data))
    
    return word_list


def update_word_review_status_service(word_id: str, difficulty: str, user_id: str) -> Optional[dict]:
    """更新单词的复习状态"""
    # 查找单词
    word = words.find_one({"_id": ObjectId(word_id), "user_id": user_id})
    if not word:
        return None
    
    # 根据难度级别计算下次复习时间
    now = datetime.utcnow()
    review_count = word.get("review_count", 0) + 1
    
    # 根据艾宾浩斯遗忘曲线和难度调整下次复习时间
    if difficulty == "easy":
        # 简单的单词，间隔时间更长
        next_review_days = {
            1: 3,   # 第一次复习后3天
            2: 7,   # 第二次复习后7天
            3: 14,  # 第三次复习后14天
            4: 30,  # 第四次复习后30天
        }.get(review_count, 60)  # 默认60天
    elif difficulty == "medium":
        # 一般难度的单词
        next_review_days = {
            1: 1,   # 第一次复习后1天
            2: 3,   # 第二次复习后3天
            3: 7,   # 第三次复习后7天
            4: 14,  # 第四次复习后14天
        }.get(review_count, 30)  # 默认30天
    else:  # difficult
        # 困难的单词，间隔时间更短
        next_review_days = {
            1: 0.5,  # 第一次复习后12小时
            2: 1,    # 第二次复习后1天
            3: 3,    # 第三次复习后3天
            4: 7,    # 第四次复习后7天
        }.get(review_count, 14)  # 默认14天
    
    # 计算下次复习时间
    next_review = now + timedelta(days=next_review_days)
    
    # 更新单词
    update_data = {
        "last_reviewed": now,
        "next_review": next_review,
        "review_count": review_count
    }
    
    words.update_one(
        {"_id": ObjectId(word_id)},
        {"$set": update_data}
    )
    
    # 获取更新后的单词
    updated_word = words.find_one({"_id": ObjectId(word_id)})
    if not updated_word:
        return None
    
    # 转换为API模型
    word_data = {
        "id": str(updated_word.pop("_id")),
        "user_id": updated_word.get("user_id", ""),
        "name": updated_word.get("word", ""),  # 将 word 字段映射到 name
        "trans": updated_word.get("translation", []),  # 将 translation 字段映射到 trans
        "usphone": updated_word.get("usphone", None),
        "ukphone": updated_word.get("ukphone", None),
        "definition": updated_word.get("definition", None),
        "example": updated_word.get("example", None),
        "category": updated_word.get("category", None),
        "favorite": updated_word.get("favorite", False),
        "learned": updated_word.get("learned", False),
        "created_at": updated_word.get("created_at", datetime.utcnow()),
        "last_reviewed": updated_word.get("last_reviewed", None),
        "review_count": updated_word.get("review_count", 0)
    }
    
    return Word(**word_data)