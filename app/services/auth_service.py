from typing import Optional
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud.user import user as user_crud
from app.crud.account import create_account, get_accounts_by_user, get_account_by_id, update_account, delete_account
from app.api.v1.schemas import UserCreate, Token
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import User
from app.core.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

class AuthService:
    @staticmethod
    def register(db: Session, user_in: UserCreate) -> User:
        logger.info(f"Registering user with email={user_in.email}")
        if user_crud.get_by_email(db, email=user_in.email):
            logger.error(f"Email {user_in.email} already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if user_crud.get_by_username(db, username=user_in.username):
            logger.error(f"Username {user_in.username} already taken")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        user = user_crud.create(db, obj_in=user_in)
        logger.info(f"User registered successfully: user_id={user.user_id}")
        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> Token:
        logger.info(f"Attempting login for email={email}")
        db_user = user_crud.get_by_email(db, email=email)
        if not db_user or not verify_password(password, db_user.password_hash):
            logger.error(f"Login failed for email={email}: Incorrect email or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": str(db_user.user_id)})
        logger.info(f"Login successful for user_id={db_user.user_id}, token generated")
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        logger.info(f"Validating token: {token[:10]}...")
        token_data = decode_access_token(token)
        if token_data is None:
            logger.error("Invalid authentication credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        db_user = user_crud.get(db, id=token_data.user_id)
        if db_user is None:
            logger.error(f"User not found for user_id={token_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Token validated, user_id={db_user.user_id}")
        return db_user

    # Account Methods
    @staticmethod
    def create_account(db: Session, user_id: int, account_data: dict):
        logger.info(f"Creating account for user_id={user_id}, data={account_data}")
        try:
            account = create_account(db, user_id, account_data)
            logger.info(f"Account created: account_id={account.account_id}")
            return account
        except ValueError as e:
            logger.error(f"Failed to create account: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def get_accounts(db: Session, user_id: int, is_active: bool | None = None):
        logger.info(f"Fetching accounts for user_id={user_id}, is_active={is_active}")
        accounts = get_accounts_by_user(db, user_id, is_active)
        logger.info(f"Fetched {len(accounts)} accounts for user_id={user_id}")
        return accounts

    @staticmethod
    def get_account(db: Session, account_id: int, user_id: int):
        logger.info(f"Fetching account_id={account_id} for user_id={user_id}")
        account = get_account_by_id(db, account_id, user_id)
        if not account:
            logger.error(f"Account_id={account_id} not found or user_id={user_id} lacks permission")
            raise HTTPException(status_code=404, detail="Account not found or you don't have permission")
        logger.info(f"Found account: {account.__dict__}")
        return account

    @staticmethod
    def update_account(db: Session, account_id: int, user_id: int, update_data: dict):
        logger.info(f"Updating account_id={account_id} for user_id={user_id}, update_data={update_data}")
        account = get_account_by_id(db, account_id, user_id)
        if not account:
            logger.error(f"Account_id={account_id} not found or user_id={user_id} lacks permission")
            raise HTTPException(status_code=404, detail="Account not found or you don't have permission")
        account = update_account(db, account, update_data)
        logger.info(f"Account updated: {account.__dict__}")
        return account

    @staticmethod
    def delete_account(db: Session, account_id: int, user_id: int):
        logger.info(f"Deactivating account_id={account_id} for user_id={user_id}")
        account = get_account_by_id(db, account_id, user_id)
        if not account:
            logger.error(f"Account_id={account_id} not found or user_id={user_id} lacks permission")
            raise HTTPException(status_code=404, detail="Account not found or you don't have permission")
        account = delete_account(db, account)
        logger.info(f"Account_id={account_id} deactivated")
        return account