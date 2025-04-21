import socketio
from fastapi import FastAPI
from app.core.security import jwt
from config import Config

# 创建Socket.IO服务器
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=Config.CORS_ORIGINS
)

# 创建ASGI应用
sio_app = socketio.ASGIApp(sio)

# 连接事件
@sio.event
async def connect(sid, environ, auth):
    if not auth or "token" not in auth:
        await sio.disconnect(sid)
        return
    
    try:
        # 验证token
        payload = jwt.decode(auth["token"], Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            await sio.disconnect(sid)
            return
        
        # 保存用户ID到会话
        await sio.save_session(sid, {"user_id": user_id})
        
        # 加入聊天室
        session_id = environ.get("HTTP_QUERY_STRING", "").split("=")[1] if "=" in environ.get("HTTP_QUERY_STRING", "") else None
        if session_id:
            await sio.enter_room(sid, f"session_{session_id}")
    except Exception as e:
        print(f"Socket connection error: {e}")
        await sio.disconnect(sid)

# 断开连接事件
@sio.event
async def disconnect(sid):
    pass

# 消息事件
@sio.event
async def message(sid, data):
    session = await sio.get_session(sid)
    user_id = session.get("user_id")
    
    if not user_id or not data or "content" not in data:
        return
    
    # 处理消息
    from app.services.chat import process_message
    response = await process_message(user_id, data["content"])
    
    # 发送AI回复
    await sio.emit("message", response, room=sid)