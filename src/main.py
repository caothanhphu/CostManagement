from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Annotated
import uvicorn
from src.config import supabase
from src.services.auth_service import AuthService

"""
app = FastAPI()

# Initialize Supabase client
url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY
supabase: Client = create_client(url, key)

# Global instance of AuthService
auth_service = AuthService(supabase)

# Pydantic models for request bodies
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    data: Optional[dict] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    default_currency: Optional[str] = None


# API router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


# Dependency to get the AuthService instance
def get_auth_service():
    return auth_service


# API endpoints
@auth_router.post("/signup")
def signup(request: SignUpRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        user, session = auth_service.signup(request.email, request.password, request.data)
        return {"user": user, "session": session}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/login")
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        user, session = auth_service.login(request.email, request.password)
        return {"user": user, "session": session}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@auth_router.post("/logout")
def logout(auth_service: AuthService = Depends(get_auth_service), session=Depends(auth_service.get_current_user)):
    try:
        auth_service.logout(session.get('access_token'))
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@auth_router.get("/user")
def get_user(auth_service: AuthService = Depends(get_auth_service), session=Depends(auth_service.get_current_user)):
    try:
        return auth_service.get_user(session.get('access_token'))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@auth_router.put("/profile")
def update_profile(request: ProfileUpdateRequest, auth_service: AuthService = Depends(get_auth_service), session=Depends(auth_service.get_current_user)):
    try:
        user_id = session.get("user").get('id')
        return auth_service.update_profile(user_id, request.full_name, request.default_currency)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Include the router in the main app
app.include_router(auth_router)
"""
