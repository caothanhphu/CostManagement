from sqlalchemy import Boolean, Column, BigInteger, String, DateTime, func
from sqlalchemy.orm import relationship
from .account import Base  # Import Base từ account.py

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    default_currency = Column(String(3), nullable=False, default="VND")
    is_active = Column(Boolean, nullable=False, default=False)  # Thêm trường is_active
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    accounts = relationship("Account", back_populates="user")