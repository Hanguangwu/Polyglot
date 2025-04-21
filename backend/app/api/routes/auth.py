from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, get_current_user, get_password_hash
from app.models.user import UserCreate, User, Token, UserUpdate, UserInDB  # 添加 UserInDB 导入
from app.services.user import create_user, authenticate_user, update_user, change_password
from config import Config

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    return create_user(user)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        # 确保使用字符串形式的 ID
        user_id = str(user.id) if hasattr(user, "id") else str(user._id)
        
        access_token = create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"登录错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录过程中发生错误: {str(e)}"
        )
@router.get("/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    return User.from_db_model(current_user)

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    return update_user(current_user.id, user_update)

@router.post("/change-password", response_model=bool)
async def update_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user)
):
    return change_password(current_user.id, old_password, new_password)