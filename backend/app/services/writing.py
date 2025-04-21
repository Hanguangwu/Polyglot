from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import json
from app.core.database import writings
from app.models.writing import WritingCreate, WritingUpdate
from fastapi import HTTPException, status
import openai
from config import Config
import re
from redlines import Redlines

# 配置OpenAI API
openai.api_key = Config.OPENAI_API_KEY
openai.base_url = Config.OPENAI_API_BASE

def get_writings_by_user(user_id: str) -> List[dict]:
    """获取用户的所有写作"""
    cursor = writings.find({"user_id": user_id}).sort("created_at", -1)
    result = []
    for writing in cursor:
        writing["id"] = str(writing.pop("_id"))
        result.append(writing)
    return result

def get_writing_by_id(writing_id: str, user_id: str) -> Optional[dict]:
    """根据ID获取写作"""
    writing = writings.find_one({"_id": ObjectId(writing_id), "user_id": user_id})
    if writing:
        writing["id"] = str(writing.pop("_id"))
        # 确保返回反馈信息
        writing["feedback"] = writing.get("feedback", "")
    return writing

def create_writing(writing: WritingCreate, user_id: str) -> dict:
    """创建新写作"""
    writing_dict = writing.model_dump()
    writing_dict["user_id"] = user_id
    writing_dict["created_at"] = datetime.utcnow()
    
    result = writings.insert_one(writing_dict)
    created = writings.find_one({"_id": result.inserted_id})
    
    # 添加错误处理，确保找到了文档
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created writing"
        )
    
    created["id"] = str(created.pop("_id"))
    return created

def update_writing(writing_id: str, writing_update: WritingUpdate, user_id: str) -> Optional[dict]:
    """更新写作"""
    writing = writings.find_one({"_id": ObjectId(writing_id), "user_id": user_id})
    if not writing:
        return None
    
    # 确保所有字段都能正确保存
    update_data = {k: v for k, v in writing_update.model_dump().items() if v is not None}
    
    # 记录更新时间
    update_data["updated_at"] = datetime.utcnow()
    
    if update_data:
        writings.update_one({"_id": ObjectId(writing_id)}, {"$set": update_data})
        
    updated = writings.find_one({"_id": ObjectId(writing_id)})
    
    # 添加错误处理，确保找到了文档
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated writing"
        )
    
    updated["id"] = str(updated.pop("_id"))
    return updated

def delete_writing(writing_id: str, user_id: str) -> bool:
    """删除写作"""
    result = writings.delete_one({"_id": ObjectId(writing_id), "user_id": user_id})
    return result.deleted_count > 0

def check_writing(content: str, topic: str) -> dict:
    """检查写作并提供反馈"""
    prompt = f"""
    你是一位IELTS学术写作考试的评分专家。请根据IELTS学术写作考试的评分标准，对以下Task 2作文进行评分和分析。

    评分标准包括四个方面，每个方面占总分的25%：
    1. 任务回应（Task Response）
    2. 连贯与衔接（Coherence and Cohesion）
    3. 词汇资源（Lexical Resource）
    4. 语法范围与准确性（Grammatical Range and Accuracy）

    请提供以下内容：
    1. 每个评分标准的得分（满分9分）和详细分析
    2. 总体得分（四个方面的平均分）
    3. 详细的改进建议，包括语法错误、词汇使用、结构组织等方面
    4. 根据同样的题目，提供一篇满分范文

    作文题目：{topic}

    学生作文：
    {content}

    请以Markdown格式输出你的分析和建议，并使用表格展示评分。
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an IELTS writing examiner who provides detailed feedback and scoring."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        feedback = response.choices[0].message.content
        
        # 确保feedback不为None
        if not feedback:
            feedback = ""
            print("Warning: Empty feedback received from OpenAI")
        
        # 提取分数 - 改进正则表达式以匹配更多可能的格式
        score_pattern = r"总体得分[:：]?\s*(\d+\.?\d*)|总分[:：]?\s*(\d+\.?\d*)"
        score_match = re.search(score_pattern, feedback)
        score = None
        if score_match:
            # 获取第一个非None的匹配组
            for group in score_match.groups():
                if group:
                    score = float(group)
                    break
        
        # 如果没有找到分数，尝试从表格中提取
        if not score:
            table_score_pattern = r"\|\s*总[分数]?\s*\|\s*(\d+\.?\d*)\s*\|"
            table_match = re.search(table_score_pattern, feedback)
            if table_match and table_match.group(1):
                score = float(table_match.group(1))
        
        # 使用redlines标记语法错误
        grammar_errors = extract_grammar_errors(feedback, content)
        
        # 从反馈中提取模范作文
        model_essay = extract_model_essay(feedback)
        
        # 如果没有找到模范作文，尝试使用不同的正则表达式
        if not model_essay:
            model_section_pattern = r"(# 满分范文|## 满分范文|### 满分范文|# 模范作文|## 模范作文|### 模范作文)(.*?)(?=# |## |### |$)"
            model_section = re.search(model_section_pattern, feedback, re.DOTALL)
            if model_section and len(model_section.groups()) >= 2:
                model_essay = model_section.group(2).strip()
        
        # 创建带有redlines标记的修改后内容
        corrected_content = ""
        if grammar_errors:
            diff = Redlines(content, apply_corrections(content, grammar_errors))
            corrected_content = diff.output_markdown
        
        # 确保所有字段都有值，即使是空值
        return {
            "feedback": feedback,
            "score": score if score else 0.0,  # 提供默认值
            "corrected_content": corrected_content or content,
            "model_essay": model_essay or "未能生成范文。"
        }
    
    except Exception as e:
        print(f"Error in check_writing: {str(e)}")  # 添加调试日志
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking writing: {str(e)}"
        )

def extract_grammar_errors(feedback: str, original_content: str) -> List[dict]:
    """从反馈中提取语法错误"""
    errors = []
    
    # 确保feedback不为None
    if not feedback:
        return errors
    
    # 查找语法错误部分 - 改进正则表达式以匹配更多可能的格式
    grammar_section_pattern = r"(语法范围与准确性|语法错误|Grammar).*?(?=##|#|\Z)"
    grammar_section = re.search(grammar_section_pattern, feedback, re.DOTALL)
    if grammar_section:
        grammar_text = grammar_section.group(0)
        
        # 查找错误示例，支持多种格式
        patterns = [
            r"[错误|误][:：]\s*([^\n]+?)\s*[->→]\s*[正确|对][:：]\s*([^\n]+)",  # 错误: xxx -> 正确: yyy
            r"([^\n]+?)\s*[->→]\s*([^\n]+)",  # xxx -> yyy
            r"应该是[：:]\s*([^\n]+?)\s*而不是[：:]\s*([^\n]+)"  # 应该是: xxx 而不是: yyy
        ]
        
        for pattern in patterns:
            error_matches = re.finditer(pattern, grammar_text)
            for match in error_matches:
                if len(match.groups()) >= 2:  # 确保有足够的匹配组
                    wrong = match.group(1).strip()
                    correct = match.group(2).strip()
                    
                    # 确保错误文本在原文中存在
                    if wrong in original_content:
                        errors.append({
                            "wrong": wrong,
                            "correct": correct
                        })
    
    return errors

def apply_corrections(text: str, errors: List[dict]) -> str:
    """应用语法错误修正"""
    corrected = text
    for error in errors:
        corrected = corrected.replace(error["wrong"], error["correct"])
    return corrected
def extract_model_essay(feedback: str) -> str:
    """从反馈中提取模范作文"""
    # 确保feedback不为None
    if not feedback:
        return ""
        
    # 尝试多种可能的标题格式
    patterns = [
        r"(满分范文|模范作文|示例作文|Sample Essay|Model Essay)[:：]?\s*(.*?)(?=##|#|\Z)",
        r"(# 满分范文|## 满分范文|### 满分范文|# 模范作文|## 模范作文)(.*?)(?=# |## |### |\Z)",
        r"(4\.\s*[根据同样的题目，]*提供一篇满分范文)(.*?)(?=##|#|\Z)"
    ]
    
    for pattern in patterns:
        model_section = re.search(pattern, feedback, re.DOTALL)
        if model_section and len(model_section.groups()) >= 2:  # 确保有足够的匹配组
            return model_section.group(2).strip()
    
    # 如果没有找到明确的标题，尝试查找最后一个段落
    paragraphs = feedback.split("\n\n")
    if len(paragraphs) > 1 and len(paragraphs[-1].strip()) > 100:  # 假设范文至少有100个字符
        return paragraphs[-1].strip()
    
    return ""