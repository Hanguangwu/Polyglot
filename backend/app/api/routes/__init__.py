from fastapi import APIRouter
from app.api.routes import auth, words, chat, writing

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(words.router, prefix="/words", tags=["words"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(writing.router, prefix="/writing", tags=["writing"])