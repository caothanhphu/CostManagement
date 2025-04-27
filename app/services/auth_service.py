from typing import Optional
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud.user import user as user_crud
from app.crud.account import create_account, get_accounts_by_user, get_account_by_id, update_account, delete_account
from app.api.v1.schemas import UserCreate, Token
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import User

class AuthService:
    @staticmethod
    def register(db: Session, user_in: UserCreate) -> User:
        # Check if email or username already exists
        if user_crud.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if user_crud.get_by_username(db, username=user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        return user_crud.create(db, obj_in=user_in)

    @staticmethod
    def login(db: Session, email: str, password: str) -> Token:
        db_user = user_crud.get_by_email(db, email=email)
        if not db_user or not verify_password(password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": str(db_user.user_id)})
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        token_data = decode_access_token(token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        db_user = user_crud.get(db, id=token_data.user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return db_user

    # Account Methods
    @staticmethod
    def create_account(db: Session, user_id: int, account_data: dict):
        account = create_account(db, user_id, account_data)
        return account

    @staticmethod
    def get_accounts(db: Session, user_id: int, is_active: bool | None = None):
        return get_accounts_by_user(db, user_id, is_active)

    @staticmethod
    def get_account(db: Session, account_id: int, user_id: int):
        account = get_account_by_id(db, account_id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found or you don't have permission")
        return account

    @staticmethod
    def update_account(db: Session, account_id: int, user_id: int, update_data: dict):
        account = get_account_by_id(db, account_id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found or you don't have permission")
        return update_account(db, account, update_data)

    @staticmethod
    def delete_account(db: Session, account_id: int, user_id: int):
        account = get_account_by_id(db, account_id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found or you don't have permission")
        return delete_account(db, account)