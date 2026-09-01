from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.auth.deps import CurrentUser, DbSession
from app.api.auth.auth import get_password_hash
from app.db.models.admin import Admin
from app.db.models.site import Site

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/me")
async def read_users_me(current_user: CurrentUser):
    return current_user
