from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server settings
    port: int = 8000
    
    # Supabase settings
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    
    # AI service API keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "1SM7GgM6IMuvQlz2BwM3"
    
    # Feature flags
    enable_dubbing: bool = True
    
    # External services
    klap_api_key: str
    agentmail_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
