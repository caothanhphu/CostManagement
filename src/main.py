# src/main.py

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Header, Query 
from pydantic import BaseModel, EmailStr, Field 
from typing import Optional, Dict, Any, Annotated, List # Import Annotated
from datetime import date, datetime 
# Import AuthService của bạn
from src.services.auth_service import AuthService
# Enum types (nếu chưa có hoặc để dùng trong Pydantic)

from enum import Enum
class AccountTypeEnum(str, Enum):
    cash = 'cash'
    bank_account = 'bank_account'
    credit_card = 'credit_card'
    e_wallet = 'e_wallet'
    investment = 'investment'
    other = 'other'

class CategoryTypeEnum(str, Enum):
    expense = 'expense'
    income = 'income'

class RecurrenceFrequencyEnum(str, Enum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'
    yearly = 'yearly'
    
# --- Pydantic Models ---
# Models cho Request Bodies
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    # Sử dụng Dict để linh hoạt cho data, có thể chứa full_name
    data: Optional[Dict[str, Any]] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    default_currency: Optional[str] = None # Giả sử lưu trong bảng Users của bạn

# Models cho Response (Tùy chọn nhưng tốt cho tài liệu API)
# Bạn có thể định nghĩa chi tiết hơn dựa trên cấu trúc trả về của Supabase/AuthService
class UserSessionResponse(BaseModel):
    # Ví dụ: Dựa trên response của supabase-py (cần kiểm tra lại cấu trúc chính xác)
    user: Optional[Dict[str, Any]] = None
    session: Optional[Dict[str, Any]] = None
    message: Optional[str] = None # Cho trường hợp lỗi

class UserInfoResponse(BaseModel):
    # Ví dụ:
    id: str
    email: EmailStr
    user_metadata: Dict[str, Any]
    # ... các trường khác từ Supabase Auth user object

class ProfileResponse(BaseModel):
    # Ví dụ: Dựa trên cấu trúc bảng Users của bạn
    user_id: Any # Hoặc int/uuid tùy thiết kế DB
    username: Optional[str] = None
    email: EmailStr
    full_name: Optional[str] = None
    default_currency: Optional[str] = None
    # ... các trường khác trong bảng Users

class MessageResponse(BaseModel):
    message: str

# --- FastAPI App and Routers ---
app = FastAPI(title="Cost Management API", version="0.1.0")

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
# Tách /profile ra router riêng cho rõ ràng
profile_router = APIRouter(prefix="/profile", tags=["User Profile"])

# --- Service Instance ---
# Khởi tạo AuthService (nó sẽ tự đọc biến môi trường và tạo client Supabase)
auth_service = AuthService()

# --- Dependencies ---
# Dependency để lấy access token từ header Authorization: Bearer <token>
async def get_current_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing or invalid Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1]
    if not token:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Empty token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# --- API Endpoints ---

@auth_router.post("/signup", response_model=UserSessionResponse)
async def signup(request: SignUpRequest):
    """
    Đăng ký người dùng mới.
    """
    try:
        # Lấy full_name từ data nếu có
        full_name = request.data.get("full_name") if request.data else None
        # Gọi service signup
        response_dict = auth_service.signup(request.email, request.password, full_name=full_name)

        # Kiểm tra response từ service (giả định response là dict có thể chứa lỗi)
        if response_dict.get("error"):
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_dict.get("error").get("message", "Signup failed"))
        # Trả về cấu trúc mong đợi (cần điều chỉnh dựa trên response thực tế của supabase-py)
        # Giả định response.dict() trả về cấu trúc có user và session
        return UserSessionResponse(**response_dict)
    except HTTPException as http_exc:
        raise http_exc # Re-raise HTTPException để FastAPI xử lý
    except Exception as e:
        # Log lỗi ở đây nếu cần
        print(f"Signup Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during signup: {str(e)}")

@auth_router.post("/login", response_model=UserSessionResponse)
async def login(request: LoginRequest):
    """
    Đăng nhập người dùng.
    """
    try:
        response_dict = auth_service.login(request.email, request.password)

        # Kiểm tra response từ service
        # auth.sign_in_with_password trả về GoTrueAPIResponse có thể có error
        # response.dict() có thể chứa thông tin lỗi hoặc user/session
        if response_dict.get("error"):
             # Supabase có thể trả về lỗi cụ thể hơn
             error_detail = response_dict.get("error_description") or response_dict.get("error").get("message", "Invalid login credentials")
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_detail)

        # Kiểm tra có session không (đăng nhập thành công)
        if not response_dict.get("session"):
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed, no session received.")

        return UserSessionResponse(**response_dict)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Login Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during login: {str(e)}")

@auth_router.post("/logout", response_model=MessageResponse)
async def logout(token: Annotated[str, Depends(get_current_token)]):
    """
    Đăng xuất người dùng (Auth Required).
    Yêu cầu Header: Authorization: Bearer <access_token>
    """
    try:
        response = auth_service.logout(token)
        # Kiểm tra message trả về từ service nếu cần
        if "Failed" in response.get("message", ""):
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.get("message"))
        return MessageResponse(message="Logout successful")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Logout Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during logout: {str(e)}")

@auth_router.get("/user", response_model=UserInfoResponse)
async def get_user_info(token: Annotated[str, Depends(get_current_token)]):
    """
    Lấy thông tin người dùng đang đăng nhập (Auth Required).
    Yêu cầu Header: Authorization: Bearer <access_token>
    """
    try:
        user_info_dict = auth_service.get_user(token)
        # Kiểm tra xem có thông tin user không
        user_data = user_info_dict.get("user")
        if user_data is None:
            # Có thể token hết hạn hoặc không hợp lệ dù đã qua check header
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not retrieve user information. Invalid or expired token.")

        # Map dữ liệu từ response của service sang Pydantic model
        # Cần kiểm tra cấu trúc trả về thực tế của auth_service.get_user()
        return UserInfoResponse(**user_data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Get User Info Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")


# Sử dụng router riêng cho /profile
@profile_router.put("", response_model=ProfileResponse) # Đường dẫn là /profile
async def update_user_profile(request: ProfileUpdateRequest, token: Annotated[str, Depends(get_current_token)]):
    """
    Cập nhật hồ sơ người dùng (tên, tiền tệ mặc định) (Auth Required).
    Yêu cầu Header: Authorization: Bearer <access_token>
    """
    if request.full_name is None and request.default_currency is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided for update.")

    try:
        # Gọi service update_profile, nó sẽ lấy user_id từ token
        updated_profile_data = auth_service.update_profile(
            access_token=token,
            full_name=request.full_name,
            default_currency=request.default_currency
        )
        if not updated_profile_data:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found or update failed.")

        # Map dữ liệu trả về từ DB (qua service) sang Pydantic model
        # Giả định service trả về dict khớp với bảng Users
        # Cần điều chỉnh dựa trên response thực tế của service và cấu trúc bảng Users
        return ProfileResponse(**updated_profile_data) # Giả sử service trả về dict của user đã update
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Update Profile Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during profile update: {str(e)}")

# --- Include Routers ---
app.include_router(auth_router)
app.include_router(profile_router) # Thêm router của profile

# --- (Optional) Add a root endpoint for testing ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to Cost Management API"}