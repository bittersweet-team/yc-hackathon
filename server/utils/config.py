from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    port: int = 8000
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    recording_api_url: str
    klap_api_key: str
    agentmail_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()