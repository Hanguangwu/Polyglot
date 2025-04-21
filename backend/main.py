from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, words, chat, writing
import uvicorn
import multiprocessing

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 明确指定前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 路由配置
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(words.router, prefix="/api/words", tags=["words"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(writing.router, prefix="/api/writing", tags=["writing"])


if __name__ == "__main__":
    # Windows 下需要保护入口点
    multiprocessing.freeze_support()
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        workers=1  # Windows 下建议使用单进程
    )

# if __name__ == "__main__":
#     import uvicorn
#     import signal
#     import sys

#     def signal_handler(sig, frame):
#         print('Exiting gracefully...')
#         sys.exit(0)

#     signal.signal(signal.SIGINT, signal_handler)
#     signal.signal(signal.SIGTERM, signal_handler)
#     uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)