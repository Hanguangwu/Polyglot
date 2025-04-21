import re
from datetime import datetime
from bson import ObjectId
from typing import List, Optional, Dict, Any
import json
import os
import tempfile
import wave
import speech_recognition as sr
import pyttsx3
from redlines import Redlines
import Levenshtein
import random
import base64
from app.core.database import chat_sessions
from app.models.chat import ChatSessionCreate, ChatSessionUpdate, Message
from fastapi import HTTPException, status, UploadFile
import openai
from config import Config

# 配置OpenAI API
openai.api_key = Config.OPENAI_API_KEY
openai.base_url = Config.OPENAI_API_BASE

def get_chat_sessions_by_user(user_id: str) -> List[dict]:
    """获取用户的所有聊天会话"""
    cursor = chat_sessions.find({"user_id": user_id}).sort("created_at", -1)
    result = []
    for session in cursor:
        session["id"] = str(session.pop("_id"))
        result.append(session)
    return result

def get_chat_session_by_id(session_id: str, user_id: str) -> Optional[dict]:
    """根据ID获取聊天会话"""
    session = chat_sessions.find_one({"_id": ObjectId(session_id), "user_id": user_id})
    if session:
        session["id"] = str(session.pop("_id"))
    return session

def create_chat_session(session: ChatSessionCreate, user_id: str) -> dict:
    """创建新聊天会话"""
    session_dict = session.model_dump()
    session_dict["user_id"] = user_id
    session_dict["created_at"] = datetime.utcnow()
    session_dict["messages"] = []
    
    result = chat_sessions.insert_one(session_dict)
    created = chat_sessions.find_one({"_id": result.inserted_id})
    
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created chat session"
        )
    
    created["id"] = str(created.pop("_id"))
    return created

def update_chat_session(session_id: str, session_update: ChatSessionUpdate, user_id: str) -> Optional[dict]:
    """更新聊天会话"""
    session = chat_sessions.find_one({"_id": ObjectId(session_id), "user_id": user_id})
    if not session:
        return None
    
    update_data = {k: v for k, v in session_update.model_dump().items() if v is not None}
    
    if update_data:
        chat_sessions.update_one({"_id": ObjectId(session_id)}, {"$set": update_data})
        
    updated = chat_sessions.find_one({"_id": ObjectId(session_id)})
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated chat session"
        )
    
    updated["id"] = str(updated.pop("_id"))
    return updated

def delete_chat_session(session_id: str, user_id: str) -> bool:
    """删除聊天会话"""
    result = chat_sessions.delete_one({"_id": ObjectId(session_id), "user_id": user_id})
    return result.deleted_count > 0

def add_message_to_session(session_id: str, message: Message, user_id: str) -> dict:
    """向聊天会话添加消息"""
    session = chat_sessions.find_one({"_id": ObjectId(session_id), "user_id": user_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = session.get("messages", [])
    messages.append(message.model_dump())
    
    chat_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"messages": messages}}
    )
    
    updated = chat_sessions.find_one({"_id": ObjectId(session_id)})
    updated["id"] = str(updated.pop("_id"))
    return updated

def get_ai_response(session_id: str, user_id: str) -> dict:
    """获取AI回复"""
    session = chat_sessions.find_one({"_id": ObjectId(session_id), "user_id": user_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = session.get("messages", [])
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages in chat session"
        )
    
    session_type = session.get("type", "casual")
    
    if session_type == "casual":
        return get_casual_chat_response(messages, session_id, user_id)
    elif session_type == "ielts":
        return get_ielts_speaking_response(messages, session_id, user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session type"
        )

def get_casual_chat_response(messages: List[dict], session_id: str, user_id: str) -> dict:
    """获取闲聊模式的AI回复"""
    # 检查是否是新会话，如果是则生成随机话题
    if len(messages) == 1 and messages[0]["role"] == "user":
        return generate_random_topic(messages, session_id, user_id)
    
    # 获取用户最后一条消息
    last_user_message = None
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg
            break
    
    if not last_user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message found"
        )
    
    # 构建系统提示
    system_prompt = """
    你是一位挑剔但友好的英语教师。你的任务是：
    1. 对用户的英语输入进行评判
    2. 指出语法、词汇或表达上的错误
    3. 提供一个更好的表达方式
    4. 继续对话，提出一个相关的问题或评论

    请按以下格式回复：
    1. 评价：[对用户输入的简短评价]
    2. 修正：[使用markdown格式标记错误，如果没有错误，写"你的表达很好！"]
    3. 更好的表达：[提供一个更地道的表达方式]
    4. 回应：[你对用户内容的回应，包括一个问题或评论]
    """
    
    # 准备发送给OpenAI的消息
    openai_messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # 添加历史消息，但最多只添加最近的10条
    history_messages = messages[-10:]
    for msg in history_messages:
        openai_messages.append({"role": msg["role"], "content": msg["content"]})
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        # 解析AI回复
        evaluation = ""
        correction = ""
        better_expression = ""
        reply = ""
        
        eval_match = re.search(r"评价：(.*?)(?=\n[2-4]\.|\Z)", ai_response, re.DOTALL)
        if eval_match:
            evaluation = eval_match.group(1).strip()
        
        corr_match = re.search(r"修正：(.*?)(?=\n[3-4]\.|\Z)", ai_response, re.DOTALL)
        if corr_match:
            correction = corr_match.group(1).strip()
        
        expr_match = re.search(r"更好的表达：(.*?)(?=\n4\.|\Z)", ai_response, re.DOTALL)
        if expr_match:
            better_expression = expr_match.group(1).strip()
        
        reply_match = re.search(r"回应：(.*?)(?=\Z)", ai_response, re.DOTALL)
        if reply_match:
            reply = reply_match.group(1).strip()
        
        # 使用redlines标记错误
        corrected_content = ""
        if "你的表达很好" not in correction and last_user_message["content"].strip():
            # 尝试从修正中提取错误和正确表达
            corrections = extract_corrections(correction, last_user_message["content"])
            if corrections:
                corrected_text = apply_corrections(last_user_message["content"], corrections)
                diff = Redlines(last_user_message["content"], corrected_text)
                corrected_content = diff.output_markdown
        
        # 生成语音
        audio_base64 = generate_speech(reply)
        
        # 构建AI回复消息
        ai_message = {
            "role": "assistant",
            "content": f"{evaluation}\n\n{correction}\n\n更好的表达：{better_expression}\n\n{reply}",
            "audio_url": audio_base64,
            "corrected_content": corrected_content or None
        }
        
        # 将AI回复添加到会话
        messages.append(ai_message)
        chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"messages": messages}}
        )
        
        return ai_message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI response: {str(e)}"
        )

def generate_random_topic(messages: List[dict], session_id: str, user_id: str) -> dict:
    """生成随机话题开始对话"""
    system_prompt = """
    你是一位友好的英语教师。请生成一个有趣的随机话题，并提出一个相关的问题来开始对话。
    话题应该是日常生活中常见的，适合英语学习者练习口语的话题。
    
    请直接给出话题和问题，不要有其他内容。
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请生成一个随机话题开始对话"}
            ],
            temperature=0.9,
            max_tokens=200
        )
        
        topic = response.choices[0].message.content
        
        # 生成语音
        audio_base64 = generate_speech(topic)
        
        # 构建AI回复消息
        ai_message = {
            "role": "assistant",
            "content": f"让我们开始聊天吧！\n\n{topic}",
            "audio_url": audio_base64
        }
        
        # 将AI回复添加到会话
        messages.append(ai_message)
        chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"messages": messages}}
        )
        
        return ai_message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating random topic: {str(e)}"
        )

def get_ielts_speaking_response(messages: List[dict], session_id: str, user_id: str) -> dict:
    """获取雅思口语模式的AI回复"""
    # 检查是否是新会话，如果是则生成雅思口语题目
    if len(messages) == 1 and messages[0]["role"] == "user":
        return generate_ielts_speaking_topic(messages, session_id, user_id)
    
    # 获取用户最后一条消息
    last_user_message = None
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg
            break
    
    if not last_user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message found"
        )
    
    # 构建系统提示
    system_prompt = """
    你是一位IELTS口语考官。你的任务是：
    1. 评估考生的口语回答
    2. 提供详细的反馈，包括流利度、词汇、语法和发音
    3. 给出一个分数（满分9分）
    4. 提供改进建议
    5. 提出下一个相关问题

    请按以下格式回复：
    1. 评分：[分数]/9
    2. 反馈：[详细反馈]
    3. 改进建议：[具体建议]
    4. 下一个问题：[相关的后续问题]
    """
    
    # 准备发送给OpenAI的消息
    openai_messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    history_messages = messages[-10:]
    for msg in history_messages:
        # 确保只包含 role 和 content 字段
        openai_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        # 解析AI回复
        score = ""
        feedback = ""
        suggestions = ""
        next_question = ""
        
        score_match = re.search(r"评分：\s*(\d+\.?\d*)\/9", ai_response)
        if score_match:
            score = score_match.group(1)
        
        feedback_match = re.search(r"反馈：(.*?)(?=\n[3-4]\.|\Z)", ai_response, re.DOTALL)
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        
        suggestions_match = re.search(r"改进建议：(.*?)(?=\n4\.|\Z)", ai_response, re.DOTALL)
        if suggestions_match:
            suggestions = suggestions_match.group(1).strip()
        
        question_match = re.search(r"下一个问题：(.*?)(?=\Z)", ai_response, re.DOTALL)
        if question_match:
            next_question = question_match.group(1).strip()
        
        # 生成语音
        audio_base64 = generate_speech(next_question)
        
        # 构建AI回复消息
        ai_message = {
            "role": "assistant",
            "content": f"评分：{score}/9\n\n反馈：{feedback}\n\n改进建议：{suggestions}\n\n下一个问题：{next_question}",
            "audio_url": audio_base64
        }
        
        # 将AI回复添加到会话
        messages.append(ai_message)
        chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"messages": messages}}
        )
        
        return ai_message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI response: {str(e)}"
        )

def generate_ielts_speaking_topic(messages: List[dict], session_id: str, user_id: str) -> dict:
    """生成雅思口语题目开始对话"""
    system_prompt = """
    你是一位IELTS口语考官。请生成一个雅思口语Part 2的话题卡片，并提出相关的问题。
    
    请按以下格式回复：
    
    # IELTS Speaking Part 2
    
    请描述：[话题]
    
    你应该说：
    - [要点1]
    - [要点2]
    - [要点3]
    - [要点4]
    
    你有1分钟准备，2分钟回答。准备好后请开始回答。
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请生成一个雅思口语Part 2的话题"}
            ],
            temperature=0.8,
            max_tokens=300
        )
        
        topic = response.choices[0].message.content
        
        # 生成语音
        audio_base64 = generate_speech(topic)
        
        # 构建AI回复消息
        ai_message = {
            "role": "assistant",
            "content": topic,
            "audio_url": audio_base64
        }
        
        # 将AI回复添加到会话
        messages.append(ai_message)
        chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"messages": messages}}
        )
        
        return ai_message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating IELTS speaking topic: {str(e)}"
        )

def process_audio(audio_file: UploadFile, session_id: str, user_id: str) -> dict:
    """处理用户上传的音频文件"""
    session = chat_sessions.find_one({"_id": ObjectId(session_id), "user_id": user_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # 获取最后一条AI消息作为参考文本
    messages = session.get("messages", [])
    last_ai_message = None
    for msg in reversed(messages):
        if msg["role"] == "assistant":
            last_ai_message = msg
            break
    
    if not last_ai_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No AI message found for reference"
        )
    
    # 保存上传的音频文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_file.file.read())
        temp_file_path = temp_file.name
    
    try:
        # 使用语音识别将音频转换为文本
        recognized_text = recognize_speech_from_audio(temp_file_path)
        
        if not recognized_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not recognize speech from audio"
            )
        
        # 评估准确度
        session_type = session.get("type", "casual")
        if session_type == "ielts":
            # 对于雅思口语，我们需要评估回答的质量
            evaluation_result = evaluate_ielts_speaking(recognized_text, last_ai_message["content"])
            score = evaluation_result.get("score", 0)
            feedback = evaluation_result.get("feedback", "")
        else:
            # 对于闲聊，我们只需要简单评估语音识别的准确度
            score = None
            feedback = None
        
        # 创建用户消息
        user_message = {
            "role": "user",
            "content": recognized_text,
            "score": score,
            "feedback": feedback
        }
        
        # 将用户消息添加到会话
        messages.append(user_message)
        chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"messages": messages}}
        )
        
        return user_message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio: {str(e)}"
        )
    finally:
        # 删除临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def recognize_speech_from_audio(filename: str) -> Optional[str]:
    """从音频文件中识别语音"""
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not access speech recognition service"
            )

def evaluate_ielts_speaking(recognized_text: str, reference_text: str) -> Dict[str, Any]:
    """评估雅思口语回答的质量"""
    system_prompt = f"""
    你是一位IELTS口语评分专家。请根据以下题目和考生的回答，给出评分和反馈。
    
    题目：
    {reference_text}
    
    考生回答：
    {recognized_text}
    
    请评估以下几个方面：
    1. 流利度和连贯性
    2. 词汇资源
    3. 语法范围和准确性
    4. 发音
    
    请给出一个总体分数（满分9分）和详细的反馈。
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an IELTS speaking examiner."},
                {"role": "user", "content": system_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        evaluation = response.choices[0].message.content
        
        # 提取分数
        score_match = re.search(r"(\d+\.?\d*)\/9", evaluation)
        score = float(score_match.group(1)) if score_match else 5.0
        
        return {
            "score": score,
            "feedback": evaluation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating IELTS speaking: {str(e)}"
        )

def extract_corrections(correction_text: str, original_text: str) -> List[Dict[str, str]]:
    """从修正文本中提取错误和正确表达"""
    corrections = []
    
    # 尝试匹配常见的错误标记格式
    # 例如："错误: xxx -> 正确: yyy" 或 "~~xxx~~ should be *yyy*"
    patterns = [
        r"~~(.*?)~~\s*(?:应该是|should be)\s*\*(.*?)\*",
        r"\"(.*?)\"\s*(?:应该是|should be)\s*\"(.*?)\"",
        r"'(.*?)'\s*(?:应该是|should be)\s*'(.*?)'",
        r"错误[:：]\s*(.*?)\s*(?:->|→)\s*正确[:：]\s*(.*?)(?=\n|$)"
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, correction_text, re.MULTILINE)
        for match in matches:
            wrong = match.group(1).strip()
            correct = match.group(2).strip()
            if wrong in original_text:
                corrections.append({
                    "wrong": wrong,
                    "correct": correct
                })
    
    return corrections

def apply_corrections(text: str, corrections: List[Dict[str, str]]) -> str:
    """应用修正到原文本"""
    corrected = text
    for correction in corrections:
        corrected = corrected.replace(correction["wrong"], correction["correct"])
    return corrected

def generate_speech(text: str) -> str:
    """生成语音并返回base64编码的音频数据"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file_path = temp_file.name
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # 使用女声
        for voice in voices:
            if "female" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.save_to_file(text, temp_file_path)
        engine.runAndWait()
        
        # 读取音频文件并转换为base64
        with open(temp_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
            base64_audio = base64.b64encode(audio_data).decode("utf-8")
            
        return f"data:audio/wav;base64,{base64_audio}"
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating speech: {str(e)}"
        )
    finally:
        # 删除临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)