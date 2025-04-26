import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Config:
    def __init__(self):
        self.SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
        self.SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)