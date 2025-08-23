import httpx
import asyncio
from typing import Optional
from utils.config import settings
from utils.supabase_client import get_supabase_client
import logging
import os
import uuid
from pydantic import HttpUrl

logger = logging.getLogger(__name__)

class RecordingService:
    def __init__(self):
        self.api_url = settings.recording_api_url
        self.use_mock = settings.use_mock_recording or settings.recording_api_url == "mock"
        
    async def record_demo(self, url: str, instruction: str) -> Optional[str]:
        """
        Record a demo video of a website
        Returns the URL of the recorded video
        """
        # MOCK MODE: Upload sample.mp4 to Supabase Storage for testing
        if self.use_mock:
            logger.info(f"MOCK MODE: Using sample video instead of recording {url}")
            return await self._upload_sample_video()
        
        # PRODUCTION MODE: Call actual recording API
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/record",
                    json={
                        "url": url,
                        "width": 1920,
                        "height": 1080,
                        "format": "mp4",
                        "instruction": instruction
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
    
    async def _upload_sample_video(self) -> Optional[str]:
        """
        Upload sample.mp4 to Supabase Storage for testing
        """
        try:
            sample_path = os.path.join(os.path.dirname(__file__), "../res/sample.mp4")
            
            # Check if sample file exists
            if not os.path.exists(sample_path):
                logger.error(f"Sample video not found at {sample_path}")
                logger.info("Please place a sample.mp4 file in server/res/ directory")
                # Return a placeholder URL for testing
                return "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            
            # Read the sample video file
            with open(sample_path, "rb") as f:
                video_data = f.read()
            
            # Generate unique filename
            filename = f"demos/{uuid.uuid4()}/recording.mp4"
            
            # Upload to Supabase Storage
            supabase = get_supabase_client()
            response = supabase.storage.from_("demo-videos").upload(
                filename,
                video_data,
                file_options={"content-type": "video/mp4"}
            )
            
            # Get public URL
            public_url: HttpUrl = supabase.storage.from_("demo-videos").get_public_url(filename)
            
            logger.info(f"Sample video uploaded to: {public_url}")
            return str(public_url)
            
        except Exception as e:
            logger.error(f"Failed to upload sample video: {str(e)}")
            # Return a public sample video URL as fallback
            return "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    
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
