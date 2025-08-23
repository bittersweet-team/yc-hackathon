"""
Pydantic models for Klap API
Based on official documentation: https://docs.klap.app/
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class TaskType(str, Enum):
    VIDEO_TO_SHORTS = "video-to-shorts"
    VIDEO_TO_VIDEO = "video-to-video"


class TaskStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class OutputType(str, Enum):
    PROJECT = "project"
    FOLDER = "folder"


class ExportStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


# Request Models
class EditingOptions(BaseModel):
    """Editing options for video processing"""
    reframe: Optional[bool] = True
    emojis: Optional[bool] = True
    intro_title: Optional[bool] = True
    remove_silences: Optional[bool] = False
    captions: Optional[bool] = True
    caption_style: Optional[str] = "default"


class VideoToShortsRequest(BaseModel):
    """Request body for video-to-shorts task"""
    source_video_url: HttpUrl = Field(..., description="URL of the source video")
    language: Optional[str] = Field("en", description="Language code (e.g., 'en', 'es', 'fr')")
    max_duration: Optional[int] = Field(30, ge=15, le=90, description="Maximum duration of each clip in seconds")
    max_clip_count: Optional[int] = Field(10, ge=1, le=20, description="Maximum number of clips to generate")
    editing_options: Optional[EditingOptions] = Field(default_factory=EditingOptions)
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_video_url": "https://youtube.com/watch?v=example",
                "language": "en",
                "max_duration": 60,
                "max_clip_count": 5,
                "editing_options": {
                    "reframe": True,
                    "emojis": True,
                    "intro_title": True,
                    "remove_silences": False
                }
            }
        }


class VideoToVideoRequest(BaseModel):
    """Request body for video-to-video task"""
    source_video_url: HttpUrl = Field(..., description="URL of the source video")
    language: Optional[str] = Field("en", description="Language code")
    editing_options: Optional[EditingOptions] = Field(default_factory=EditingOptions)


class WatermarkConfig(BaseModel):
    """Watermark configuration for exports"""
    src_url: HttpUrl = Field(..., description="URL of the watermark image")
    pos_x: Optional[float] = Field(0.9, ge=0, le=1, description="X position (0-1)")
    pos_y: Optional[float] = Field(0.9, ge=0, le=1, description="Y position (0-1)")
    scale: Optional[float] = Field(0.1, ge=0.01, le=1, description="Scale factor")


class ExportRequest(BaseModel):
    """Request body for creating an export"""
    watermark: Optional[WatermarkConfig] = None
    preset: Optional[str] = Field("tiktok", description="Export preset (tiktok, youtube, instagram)")
    resolution: Optional[str] = Field("1080x1920", description="Video resolution")
    format: Optional[Literal["mp4", "mov"]] = Field("mp4", description="Video format")


# Response Models
class TaskObject(BaseModel):
    """Task object returned by the API"""
    id: str = Field(..., description="Task ID")
    type: TaskType = Field(..., description="Task type")
    status: TaskStatus = Field(..., description="Current task status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    output_type: OutputType = Field(..., description="Output type (project or folder)")
    output_id: str = Field(..., description="ID of the output (project or folder)")
    error_message: Optional[str] = Field(None, description="Error message if status is 'error'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "task_abc123",
                "type": "video-to-shorts",
                "status": "processing",
                "created_at": "2024-01-01T00:00:00Z",
                "output_type": "folder",
                "output_id": "folder_xyz789"
            }
        }


class ProjectObject(BaseModel):
    """Project object representing a generated video"""
    id: str = Field(..., description="Project ID")
    author_id: str = Field(..., description="User ID who created the project")
    folder_id: str = Field(..., description="Folder containing the project")
    name: str = Field(..., description="Project name")
    created_at: datetime = Field(..., description="Project creation timestamp")
    virality_score: float = Field(..., ge=0, le=100, description="Virality prediction score (0-1)")
    virality_score_explanation: str = Field(..., description="Explanation of the virality score")
    
    @property
    def player_url(self) -> str:
        """Get the player/embed URL for this project"""
        return f"https://klap.app/player/{self.id}"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "project_123",
                "author_id": "user_456",
                "folder_id": "folder_789",
                "name": "My Short Video",
                "created_at": "2024-01-01T00:00:00Z",
                "virality_score": 0.85,
                "virality_score_explanation": "High engagement potential due to trending topic"
            }
        }


class ExportObject(BaseModel):
    """Export object representing an export task"""
    id: str = Field(..., description="Export ID")
    status: ExportStatus = Field(..., description="Current export status")
    src_url: Optional[HttpUrl] = Field(None, description="URL of the exported video when ready")
    project_id: str = Field(..., description="ID of the source project")
    created_at: datetime = Field(..., description="Export creation timestamp")
    finished_at: Optional[datetime] = Field(None, description="Export completion timestamp")
    name: str = Field(..., description="Export name")
    author_id: str = Field(..., description="User ID who created the export")
    folder_id: str = Field(..., description="Folder containing the project")
    descriptions: Optional[str] = Field(None, description="Export descriptions")
    error_message: Optional[str] = Field(None, description="Error message if status is 'error'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "export_abc",
                "status": "ready",
                "src_url": "https://cdn.klap.app/videos/export_abc.mp4",
                "project_id": "project_123",
                "created_at": "2024-01-01T00:00:00Z",
                "finished_at": "2024-01-01T00:05:00Z",
                "name": "TikTok Export",
                "author_id": "user_456",
                "folder_id": "folder_789",
                "descriptions": "Exported for TikTok"
            }
        }


# List Response Models
class ProjectListResponse(BaseModel):
    """Response containing a list of projects"""
    projects: List[ProjectObject] = Field(default_factory=list)
    folder_id: str
    total_count: Optional[int] = None


class ExportListResponse(BaseModel):
    """Response containing a list of exports"""
    exports: List[ExportObject] = Field(default_factory=list)
    total_count: Optional[int] = None


# Error Response
class ErrorResponse(BaseModel):
    """Error response from the API"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
