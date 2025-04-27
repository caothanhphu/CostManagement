from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.schemas import UserCreate, UserResponse, Token, LoginRequest, ChangePassword
from app.services.auth_service import AuthService
from app.core.database import get_db
from app.models.user import User
from app.api.v1.dependencies import get_current_user
from app.core.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

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

@router.get("/activate", response_model=UserResponse)
async def activate(token: str, db: Session = Depends(get_db)):
    logger.info("Received activation request")
    user = AuthService.activate_user(db, token)
    logger.info(f"Activation successful for user_id={user.user_id}")
    return user

@router.post("/reset-password/request")
async def request_reset_password(email: str, db: Session = Depends(get_db)):
    logger.info(f"Received reset password request for email={email}")
    result = AuthService.request_reset_password(db, email)
    logger.info(f"Reset password email sent for email={email}")
    return result

@router.post("/reset-password", response_model=UserResponse)
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    logger.info("Received reset password request")
    user = AuthService.reset_password(db, token, new_password)
    logger.info(f"Password reset successful for user_id={user.user_id}")
    return user

@router.post("/change-password", response_model=UserResponse)
async def change_password(
    change_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Received change password request for user_id={current_user.user_id}")
    user = AuthService.change_password(
        db, current_user, change_data.old_password, change_data.new_password
    )
    logger.info(f"Password changed successfully for user_id={user.user_id}")
    return user