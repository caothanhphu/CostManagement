from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.schemas import AccountCreate, AccountUpdate, AccountResponse
from app.services.auth_service import AuthService
from app.core.database import get_db
from app.models.user import User  # Import từ user.py
from app.api.v1.dependencies import get_current_user
from typing import List
from app.core.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account_in: AccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Received request to create account for user_id={current_user.user_id}, data={account_in.dict()}")
    account_data = account_in.dict()
    account = AuthService.create_account(db, current_user.user_id, account_data)
    logger.info(f"Created account: {account.__dict__}")
    return account

@router.get("", response_model=List[AccountResponse])
async def get_accounts(is_active: bool | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Received request to get accounts for user_id={current_user.user_id}, is_active={is_active}")
    accounts = AuthService.get_accounts(db, current_user.user_id, is_active)
    logger.info(f"Returning {len(accounts)} accounts")
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Received request to get account_id={account_id} for user_id={current_user.user_id}")
    account = AuthService.get_account(db, account_id, current_user.user_id)
    logger.info(f"Returning account: {account.__dict__}")
    return account

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: int, account_in: AccountUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Received request to update account_id={account_id} for user_id={current_user.user_id}, data={account_in.dict()}")
    update_data = account_in.dict(exclude_unset=True)
    account = AuthService.update_account(db, account_id, current_user.user_id, update_data)
    logger.info(f"Updated account: {account.__dict__}")
    return account

@router.delete("/{account_id}", status_code=status.HTTP_200_OK)
async def delete_account(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Received request to delete account_id={account_id} for user_id={current_user.user_id}")
    AuthService.delete_account(db, account_id, current_user.user_id)
    logger.info(f"Account_id={account_id} deactivated successfully")
    return {"message": "Account deactivated successfully"}