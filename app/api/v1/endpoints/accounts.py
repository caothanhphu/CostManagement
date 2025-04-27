from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.schemas import AccountCreate, AccountUpdate, AccountResponse
from app.services.auth_service import AuthService
from app.core.database import get_db
from app.models.user import User
from app.api.v1.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account_in: AccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account_data = account_in.dict()
    account = AuthService.create_account(db, current_user.user_id, account_data)
    return account

@router.get("", response_model=List[AccountResponse])
async def get_accounts(is_active: bool | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = AuthService.get_accounts(db, current_user.user_id, is_active)
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = AuthService.get_account(db, account_id, current_user.user_id)
    return account

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: int, account_in: AccountUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_data = account_in.dict(exclude_unset=True)
    account = AuthService.update_account(db, account_id, current_user.user_id, update_data)
    return account

@router.delete("/{account_id}", status_code=status.HTTP_200_OK)
async def delete_account(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    AuthService.delete_account(db, account_id, current_user.user_id)
    return {"message": "Account deactivated successfully"}