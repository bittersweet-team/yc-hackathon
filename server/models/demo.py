from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DemoStatus(str, Enum):
    PENDING = "pending"
    RECORDING = "recording"
    PROCESSING = "processing"
    GENERATING = "generating"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"

class DemoRequest(BaseModel):
    product_url: HttpUrl
    description: Optional[str] = ""
    email: Optional[str] = None

class DemoResponse(BaseModel):
    id: str
    user_id: str
    product_url: str
    description: Optional[str] = ""
    status: DemoStatus
    long_video_url: Optional[str] = None
    short_video_urls: List[str] = []
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Demo(BaseModel):
    id: str
    user_id: str
    product_url: str
    description: Optional[str] = ""
    status: DemoStatus
    long_video_url: Optional[str] = None
    short_video_urls: List[str] = []
    klap_folder_id: Optional[str] = None
    klap_project_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime