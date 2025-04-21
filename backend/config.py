import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 应用配置
    APP_NAME = "Polyglot"
    DEBUG = True
    
    # MongoDB配置
    MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("DATABASE_NAME", "polyglot")
    
    # JWT配置
    SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # 默认7天
    
    # CORS配置
    # 在 Config 类中更新 CORS_ORIGINS
    CORS_ORIGINS = [
        "http://localhost:5173",  # Vite默认端口
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # AI服务配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE_URL", "")
    XAI_API_KEY = os.getenv("XAI_API_KEY", "")
    CHATANYWHERE_API_KEY = os.getenv("CHATANYWHERE_API_KEY", "")
    CHATANYWHERE_BASE_URL = os.getenv("CHATANYWHERE_BASE_URL", "https://api.chatanywhere.tech")
    
    # 邮件配置
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 25))
    
    # API前缀
    API_PREFIX = "/api"