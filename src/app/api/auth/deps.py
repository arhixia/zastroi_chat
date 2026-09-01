from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.admin import Admin
from app.settings.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
        token: Annotated[str,Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> Admin:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ) 

    try: 
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Admin).where(Admin.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
        
    return user


CurrentUser = Annotated[Admin, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
