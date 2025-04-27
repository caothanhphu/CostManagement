from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.schemas import UserUpdate, UserResponse
from app.crud.user import user as user_crud
from app.core.database import get_db
from app.models.user import User
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.put("/", response_model=UserResponse)
async def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_crud.update(db, db_obj=current_user, obj_in=user_in)