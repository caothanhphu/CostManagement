import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT Token for authentication
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return {"user_id": int(payload.get("sub"))}
    except jwt.PyJWTError:
        return None

# Activation Token
def create_activation_token(user_id: int, expires_delta: timedelta = timedelta(hours=24)) -> str:
    data = {"sub": str(user_id), "type": "activation"}
    expire = datetime.now(timezone.utc) + expires_delta
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_activation_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "activation":
            return None
        return {"user_id": int(payload.get("sub"))}
    except jwt.PyJWTError:
        return None

# Reset Password Token
def create_reset_password_token(user_id: int, expires_delta: timedelta = timedelta(hours=1)) -> str:
    data = {"sub": str(user_id), "type": "reset_password"}
    expire = datetime.now(timezone.utc) + expires_delta
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_reset_password_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "reset_password":
            return None
        return {"user_id": int(payload.get("sub"))}
    except jwt.PyJWTError:
        return None