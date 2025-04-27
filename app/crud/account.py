from sqlalchemy.orm import Session
from app.models import Account

def create_account(db: Session, user_id: int, account_data: dict):
    # Ánh xạ dữ liệu từ account_data
    account_fields = {
        "user_id": user_id,
        "account_name": account_data["account_name"],
        "account_type": account_data["account_type"],
        "initial_balance": account_data["initial_balance"],  # Ánh xạ initial_balance thành balance
        "current_balance": account_data["initial_balance"],  # Ánh xạ current_balance thành balance
        "currency": account_data["currency"],
        "is_active": True  # Mặc định khi tạo mới
    }
    db_account = Account(**account_fields)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts_by_user(db: Session, user_id: int, is_active: bool | None = None):
    query = db.query(Account).filter(Account.user_id == user_id)
    if is_active is not None:
        query = query.filter(Account.is_active == is_active)
    return query.all()

def get_account_by_id(db: Session, account_id: int, user_id: int):
    return db.query(Account).filter(Account.account_id == account_id, Account.user_id == user_id).first()

def update_account(db: Session, account: Account, update_data: dict):
    for key, value in update_data.items():
        if value is not None:
            setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account

def delete_account(db: Session, account: Account):
    account.is_active = False
    db.commit()
    db.refresh(account)
    return account