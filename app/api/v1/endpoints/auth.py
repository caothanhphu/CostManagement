from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.schemas import UserCreate, UserResponse, Token, LoginRequest
from app.services.auth_service import AuthService
from app.core.database import get_db
from app.models.user import User
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    user = AuthService.register(db, user_in)
    return user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, login_data.email, login_data.password)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    return {"message": "Successfully logged out"}

@router.get("/user", response_model=UserResponse)
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user