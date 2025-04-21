from pymongo import MongoClient
from config import Config
import logging
from pymongo.errors import ConnectionFailure

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加错误处理和连接测试
try:
    client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    # 测试连接
    client.admin.command('ping')
    logger.info("MongoDB连接成功!")
    db = client[Config.MONGO_DB]

    # 集合
    users = db.users
    words = db.words
    chat_sessions = db.chat_sessions
    writings = db.writings

    logger.info("Successfully connected to MongoDB")
    
except ConnectionFailure as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise