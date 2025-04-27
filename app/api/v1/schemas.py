from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    default_currency: str = "VND"

class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class ChangePassword(BaseModel):
    old_password: str
    new_password: str

# Account Schemas
class AccountCreate(BaseModel):
    account_name: str
    account_type: Literal["cash", "bank_account", "credit_card", "e_wallet", "investment", "other"]
    initial_balance: float
    currency: str

class AccountUpdate(BaseModel):
    account_name: str | None = None
    account_type: Literal["cash", "bank_account", "credit_card", "e_wallet", "investment", "other"] | None = None
    is_active: bool | None = None

class AccountResponse(BaseModel):
    account_id: int
    user_id: int
    account_name: str
    account_type: str
    initial_balance: float
    current_balance: float
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True