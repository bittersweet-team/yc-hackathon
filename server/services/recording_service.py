import httpx
import asyncio
from typing import Optional
from utils.config import settings
import logging

logger = logging.getLogger(__name__)

class RecordingService:
    def __init__(self):
        self.api_url = settings.recording_api_url
        
    async def record_demo(self, url: str, duration: int = 30) -> Optional[str]:
        """
        Record a demo video of a website
        Returns the URL of the recorded video
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/record",
                    json={
                        "url": url,
                        "duration": duration,
                        "width": 1920,
                        "height": 1080,
                        "format": "mp4"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("video_url")
                else:
                    logger.error(f"Recording failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Recording service error: {str(e)}")
            return None
    
    async def check_recording_status(self, recording_id: str) -> dict:
        """
        Check the status of a recording job
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/status/{recording_id}"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "error", "message": "Failed to check status"}
                    
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return {"status": "error", "message": str(e)}

recording_service = RecordingService()