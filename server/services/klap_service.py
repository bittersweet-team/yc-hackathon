import httpx
import asyncio
from typing import List, Optional, Dict
from utils.config import settings
import logging

logger = logging.getLogger(__name__)

class KlapService:
    def __init__(self):
        self.api_key = settings.klap_api_key
        self.base_url = "https://api.klap.app"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def submit_video_for_shorts(self, video_url: str, description: str = "") -> Optional[str]:
        """
        Submit a video to Klap for short-form video generation
        Returns task_id for tracking progress
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks/video-to-shorts",
                    headers=self.headers,
                    json={
                        "source_video_url": video_url,
                        "language": "en",
                        "max_duration": 60,
                        "max_clip_count": 5,
                        "editing_options": {
                            "reframe": True,
                            "emojis": True,
                            "intro_title": True,
                            "remove_silences": False
                        },
                        "description": description
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("task_id")
                else:
                    logger.error(f"Klap submission failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Klap service error: {str(e)}")
            return None
    
    async def check_task_status(self, task_id: str) -> Dict:
        """
        Check the status of a video processing task
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "error", "message": "Failed to check status"}
                    
        except Exception as e:
            logger.error(f"Task status check error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_generated_shorts(self, folder_id: str) -> List[Dict]:
        """
        Get list of generated shorts from a folder
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects/{folder_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("projects", [])
                else:
                    logger.error(f"Failed to get shorts: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Get shorts error: {str(e)}")
            return []
    
    async def export_short(self, folder_id: str, project_id: str, preset: str = "tiktok") -> Optional[str]:
        """
        Export a short video with specific preset
        Returns export_id for tracking
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/projects/{folder_id}/{project_id}/exports",
                    headers=self.headers,
                    json={
                        "preset": preset,
                        "resolution": "1080x1920",
                        "format": "mp4"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("export_id")
                else:
                    logger.error(f"Export failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            return None
    
    async def check_export_status(self, export_id: str) -> Dict:
        """
        Check the status of an export job
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/exports/{export_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "error", "message": "Failed to check export status"}
                    
        except Exception as e:
            logger.error(f"Export status check error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def wait_for_task_completion(self, task_id: str, max_wait: int = 600) -> Dict:
        """
        Poll and wait for a task to complete
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            status = await self.check_task_status(task_id)
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                return status
            
            await asyncio.sleep(10)
        
        return {"status": "timeout", "message": "Task timed out"}
    
    async def wait_for_export_completion(self, export_id: str, max_wait: int = 300) -> Dict:
        """
        Poll and wait for an export to complete
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            status = await self.check_export_status(export_id)
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                return status
            
            await asyncio.sleep(5)
        
        return {"status": "timeout", "message": "Export timed out"}

klap_service = KlapService()