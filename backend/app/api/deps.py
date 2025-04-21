from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime
from config import Config
from app.models.user import User
from app.services.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码 JWT token
        payload = jwt.decode(
            token, 
            Config.SECRET_KEY, 
            algorithms=[Config.ALGORITHM]
        )
        
        # 获取用户 ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # 检查 token 是否过期
        exp = payload.get("exp")
        if exp is not None:
            if datetime.utcnow().timestamp() > exp:
                raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    
    # 获取用户信息
    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user