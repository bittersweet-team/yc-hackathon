from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    port: int = 8000
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    recording_api_url: str = "mock"  # Set to "mock" for testing
    klap_api_key: str
    agentmail_api_key: str
    use_mock_recording: bool = True  # Toggle mock mode for testing
    
    class Config:
        env_file = ".env"

settings = Settings()