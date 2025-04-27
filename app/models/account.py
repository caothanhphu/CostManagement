from sqlalchemy import Column, BigInteger, String, Enum, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class AccountType(enum.Enum):
    cash = "cash"
    bank_account = "bank_account"
    credit_card = "credit_card"
    e_wallet = "e_wallet"
    investment = "investment"
    other = "other"

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    initial_balance = Column(Float, nullable=False, default=0.0)
    current_balance = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="accounts")