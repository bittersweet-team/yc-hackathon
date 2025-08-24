import httpx
import asyncio
from typing import List, Optional
from utils.config import settings
from models.klap_models import (
    VideoToShortsRequest,
    VideoToVideoRequest,
    ExportRequest,
    TaskObject,
    ProjectObject,
    ExportObject,
    TaskStatus,
    ExportStatus,
    EditingOptions
)
import logging

logger = logging.getLogger(__name__)


class KlapService:
    def __init__(self):
        self.api_key = settings.klap_api_key
        self.base_url = "https://api.klap.app/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def submit_video_for_shorts(
        self, 
        video_url: str,
        *,
        language: str = "en",
        max_duration: int = 30,
        max_clip_count: int = 10,
        editing_options: Optional[EditingOptions] = None
    ) -> Optional[TaskObject]:
        """
        Submit a video to Klap for short-form video generation
        Returns TaskObject with task details
        """
        try:
            # Create request model with validation
            request = VideoToShortsRequest(
                source_video_url=video_url,
                language=language,
                max_duration=max_duration,
                max_clip_count=max_clip_count,
                editing_options=editing_options or EditingOptions()
            )

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks/video-to-shorts",
                    headers=self.headers,
                    json=request.model_dump(mode="json", exclude_none=True)
                )
                
                response.raise_for_status()
                data = response.json()
                return TaskObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Klap submission failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Klap service error: {str(e)}")
            return None
    
    async def submit_video_to_video(
        self,
        video_url: str,
        language: str = "en",
        editing_options: Optional[EditingOptions] = None
    ) -> Optional[TaskObject]:
        """
        Submit a video for single video editing (video-to-video)
        Returns TaskObject with task details
        """
        try:
            request = VideoToVideoRequest(
                source_video_url=video_url,
                language=language,
                editing_options=editing_options or EditingOptions()
            )
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks/video-to-video",
                    headers=self.headers,
                    json=request.model_dump(exclude_none=True)
                )
                
                response.raise_for_status()
                data = response.json()
                return TaskObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Video-to-video submission failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Video-to-video service error: {str(e)}")
            return None
    
    async def check_task_status(self, task_id: str) -> Optional[TaskObject]:
        """
        Check the status of a video processing task
        Returns TaskObject with current status
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                return TaskObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Task status check failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Task status check error: {str(e)}")
            return None
    
    async def get_projects(self, folder_id: str) -> List[ProjectObject]:
        """
        Get list of projects (generated shorts) from a folder
        Returns list of ProjectObject
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects/{folder_id}",
                    headers=self.headers
                )

                response.raise_for_status()
                data = response.json()

                # Handle both array response and object with projects key
                if isinstance(data, list):
                    return [ProjectObject(**project) for project in data]
                elif isinstance(data, dict) and "projects" in data:
                    return [ProjectObject(**project) for project in data["projects"]]
                else:
                    logger.warning(f"Unexpected response format: {data}")
                    return []
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get projects: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Get projects error: {str(e)}")
            return []
    
    async def get_project(self, folder_id: str, project_id: str) -> Optional[ProjectObject]:
        """
        Get a specific project from a folder
        Returns ProjectObject
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects/{folder_id}/{project_id}",
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                return ProjectObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get project: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Get project error: {str(e)}")
            return None
    
    async def get_project_direct(self, project_id: str) -> Optional[ProjectObject]:
        """
        Get a project directly without folder context
        Returns ProjectObject
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects/{project_id}",
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                return ProjectObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get project direct: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Get project direct error: {str(e)}")
            return None
    
    async def create_export(
        self, 
        folder_id: str, 
        project_id: str,
        export_request: Optional[ExportRequest] = None
    ) -> Optional[ExportObject]:
        """
        Create an export for a project
        Returns ExportObject with export details
        """
        try:
            request = export_request or ExportRequest()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/projects/{folder_id}/{project_id}/exports",
                    headers=self.headers,
                    json=request.model_dump(exclude_none=True)
                )
                
                response.raise_for_status()
                data = response.json()
                return ExportObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Export creation failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            return None
    
    async def create_export_direct(
        self,
        project_id: str,
        export_request: Optional[ExportRequest] = None
    ) -> Optional[ExportObject]:
        """
        Create an export for a project without folder context
        Returns ExportObject with export details
        """
        try:
            request = export_request or ExportRequest()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/projects/{project_id}/exports",
                    headers=self.headers,
                    json=request.model_dump(exclude_none=True)
                )
                
                response.raise_for_status()
                data = response.json()
                return ExportObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Export direct creation failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Export direct error: {str(e)}")
            return None
    
    async def get_export_status(
        self, 
        folder_id: str, 
        project_id: str, 
        export_id: str
    ) -> Optional[ExportObject]:
        """
        Check the status of an export
        Returns ExportObject with current status
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects/{folder_id}/{project_id}/exports/{export_id}",
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                return ExportObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Export status check failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Export status check error: {str(e)}")
            return None
    
    async def get_export_status_direct(
        self,
        project_id: str,
        export_id: str
    ) -> Optional[ExportObject]:
        """
        Check the status of an export without folder context
        Returns ExportObject with current status
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects/{project_id}/exports/{export_id}",
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                return ExportObject(**data)
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Export direct status check failed: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Export direct status check error: {str(e)}")
            return None
    
    async def list_all_exports(
        self,
        folder_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[ExportObject]:
        """
        List all exports, optionally filtered by folder or project
        Returns list of ExportObject
        """
        try:
            params = {}
            if folder_id:
                params["folder_id"] = folder_id
            if project_id:
                params["project_id"] = project_id
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/exports",
                    headers=self.headers,
                    params=params
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Handle both array response and object with exports key
                if isinstance(data, list):
                    return [ExportObject(**export) for export in data]
                elif isinstance(data, dict) and "exports" in data:
                    return [ExportObject(**export) for export in data["exports"]]
                else:
                    logger.warning(f"Unexpected response format: {data}")
                    return []
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to list exports: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"List exports error: {str(e)}")
            return []
    
    async def wait_for_task_completion(
        self, 
        task_id: str, 
        max_wait: int = 600,
        poll_interval: int = 10
    ) -> Optional[TaskObject]:
        """
        Poll and wait for a task to complete
        Returns final TaskObject or None if timeout/error
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            task = await self.check_task_status(task_id)
            
            if not task:
                logger.error(f"Failed to get task status for {task_id}")
                return None
            
            if task.status == TaskStatus.READY:
                return task
            elif task.status == TaskStatus.ERROR:
                logger.error(f"Task {task_id} failed: {task.error_message}")
                return task
            
            await asyncio.sleep(poll_interval)
        
        logger.error(f"Task {task_id} timed out after {max_wait} seconds")
        return None
    
    async def wait_for_export_completion(
        self,
        export: ExportObject,
        max_wait: int = 300,
        poll_interval: int = 5
    ) -> Optional[ExportObject]:
        """
        Poll and wait for an export to complete
        Returns final ExportObject or None if timeout/error
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            # Check status based on whether we have folder_id
            if export.folder_id:
                status = await self.get_export_status(
                    export.folder_id, 
                    export.project_id, 
                    export.id
                )
            else:
                status = await self.get_export_status_direct(
                    export.project_id,
                    export.id
                )
            
            if not status:
                logger.error(f"Failed to get export status for {export.id}")
                return None
            
            if status.status == ExportStatus.READY:
                return status
            elif status.status == ExportStatus.ERROR:
                logger.error(f"Export {export.id} failed: {status.error_message}")
                return status
            
            await asyncio.sleep(poll_interval)
        
        logger.error(f"Export {export.id} timed out after {max_wait} seconds")
        return None


# Global instance
klap_service = KlapService()
