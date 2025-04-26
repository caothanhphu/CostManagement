import os
from supabase import create_client, Client
from typing import Dict, Any

class AuthService:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def signup(self, email, password, full_name=None) -> Dict[str, Any]:
        data = {"full_name": full_name} if full_name else {}
        response = self.supabase.auth.sign_up(
            {"email": email, "password": password, "data": data}
        )
        return response.dict()

    def login(self, email, password) -> Dict[str, Any]:
        response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response.dict()

    def logout(self, access_token: str) -> Dict[str, str]:
        try:
          self.supabase.auth.sign_out()
          return {"message": "Successfully logged out."}
        except Exception as e:
          return {"message": f"Failed to log out: {str(e)}"}

    def get_user(self, access_token: str) -> Dict[str, Any]:
        self.supabase.auth.set_session(access_token)
        response = self.supabase.auth.get_user()
        return response.dict()

    def update_profile(self, access_token: str, full_name: str = None, default_currency: str = None) -> Dict[str, Any]:
        self.supabase.auth.set_session(access_token)
        user = self.supabase.auth.get_user().user
        user_id = user.id
        data = {}
        if full_name is not None:
            data["full_name"] = full_name
        if default_currency is not None:
            data["default_currency"] = default_currency

        if not data:
            return {"message": "No data provided to update."}
        
        response = self.supabase.table("users").update(data).eq("id", user_id).execute()
        
        return response.data[0]