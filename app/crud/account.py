from sqlalchemy.orm import Session
from app.models.account import Account
from app.core.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

def check_account_name_exists(db: Session, user_id: int, account_name: str) -> bool:
    logger.debug(f"Checking if account_name={account_name} exists for user_id={user_id}")
    exists = db.query(Account).filter(
        Account.user_id == user_id,
        Account.account_name == account_name,
        Account.is_active == True
    ).first() is not None
    logger.debug(f"Account_name={account_name} exists for user_id={user_id}: {exists}")
    return exists

def create_account(db: Session, user_id: int, account_data: dict):
    logger.debug(f"Creating account with user_id={user_id}, data={account_data}")
    
    # Kiểm tra trùng account_name
    if check_account_name_exists(db, user_id, account_data["account_name"]):
        logger.error(f"Account name {account_data['account_name']} already exists for user_id={user_id}")
        raise ValueError(f"Account name '{account_data['account_name']}' already exists for this user")

    account_fields = {
        "user_id": user_id,
        "account_name": account_data["account_name"],
        "account_type": account_data["account_type"],
        "initial_balance": account_data["initial_balance"],
        "current_balance": account_data["initial_balance"],
        "currency": account_data["currency"],
        "is_active": True
    }
    logger.debug(f"Prepared account fields: {account_fields}")
    db_account = Account(**account_fields)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    logger.debug(f"Account created: {db_account.__dict__}")
    return db_account

def get_accounts_by_user(db: Session, user_id: int, is_active: bool | None = None):
    logger.debug(f"Querying accounts for user_id={user_id}, is_active={is_active}")
    query = db.query(Account).filter(Account.user_id == user_id)
    if is_active is not None:
        query = query.filter(Account.is_active == is_active)
    accounts = query.all()
    logger.debug(f"Found {len(accounts)} accounts")
    return accounts

def get_account_by_id(db: Session, account_id: int, user_id: int):
    logger.debug(f"Querying account_id={account_id} for user_id={user_id}")
    account = db.query(Account).filter(Account.account_id == account_id, Account.user_id == user_id).first()
    logger.debug(f"Account found: {account.__dict__ if account else None}")
    return account

def update_account(db: Session, account: Account, update_data: dict):
    logger.debug(f"Updating account_id={account.account_id} with data={update_data}")
    for key, value in update_data.items():
        if value is not None:
            setattr(account, key, value)
    db.commit()
    db.refresh(account)
    logger.debug(f"Account updated: {account.__dict__}")
    return account

def delete_account(db: Session, account: Account):
    logger.debug(f"Deactivating account_id={account.account_id}")
    account.is_active = False
    db.commit()
    db.refresh(account)
    logger.debug(f"Account deactivated: {account.__dict__}")
    return account