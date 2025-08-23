import asyncio
from typing import List, Optional
from models.demo import Demo, DemoStatus
from services.recording_service import recording_service
from services.klap_service import klap_service
from services.agentmail_service import agentmail_service
from utils.supabase_client import get_supabase_client
import logging

logger = logging.getLogger(__name__)

class VideoGenerator:
    async def process_demo(self, demo_id: str, user_email: str):
        """
        Main orchestrator for demo video generation
        """
        supabase = get_supabase_client()
        
        try:
            # Get demo details
            demo_response = supabase.table("demos").select("*").eq("id", demo_id).single().execute()
            if not demo_response.data:
                logger.error(f"Demo not found: {demo_id}")
                return
            
            demo = demo_response.data
            
            # Update status to recording
            await self._update_demo_status(demo_id, DemoStatus.RECORDING)
            
            # Step 1: Record the demo video
            logger.info(f"Recording demo for {demo['product_url']}")
            recorded_video_url = await recording_service.record_demo(
                demo['product_url'],
                duration=45  # 45 seconds recording
            )
            
            if not recorded_video_url:
                await self._update_demo_status(
                    demo_id, 
                    DemoStatus.FAILED,
                    error_message="Failed to record demo video"
                )
                return
            
            # Store the long video URL
            supabase.table("demos").update({
                "long_video_url": recorded_video_url,
                "status": DemoStatus.PROCESSING.value
            }).eq("id", demo_id).execute()
            
            # Step 2: Generate shorts using Klap
            logger.info(f"Submitting video to Klap for shorts generation")
            await self._update_demo_status(demo_id, DemoStatus.GENERATING)
            
            task_id = await klap_service.submit_video_for_shorts(
                recorded_video_url,
                demo['description']
            )
            
            if not task_id:
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message="Failed to submit video to Klap"
                )
                return
            
            # Wait for Klap processing
            task_result = await klap_service.wait_for_task_completion(task_id)
            
            if task_result.get("status") != "completed":
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message=f"Klap processing failed: {task_result.get('message')}"
                )
                return
            
            # Get generated shorts
            folder_id = task_result.get("folder_id")
            if not folder_id:
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message="No folder ID returned from Klap"
                )
                return
            
            shorts = await klap_service.get_generated_shorts(folder_id)
            
            if not shorts:
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message="No shorts generated"
                )
                return
            
            # Export top shorts (up to 3)
            short_video_urls = []
            top_shorts = sorted(shorts, key=lambda x: x.get("virality_score", 0), reverse=True)[:3]
            
            for short in top_shorts:
                project_id = short.get("project_id")
                if project_id:
                    export_id = await klap_service.export_short(folder_id, project_id)
                    if export_id:
                        export_result = await klap_service.wait_for_export_completion(export_id)
                        if export_result.get("status") == "completed":
                            video_url = export_result.get("video_url")
                            if video_url:
                                short_video_urls.append(video_url)
            
            # Update demo with short video URLs
            supabase.table("demos").update({
                "short_video_urls": short_video_urls,
                "klap_folder_id": folder_id,
                "status": DemoStatus.SENDING.value
            }).eq("id", demo_id).execute()
            
            # Step 3: Send email with videos
            logger.info(f"Sending demo videos to {user_email}")
            await self._update_demo_status(demo_id, DemoStatus.SENDING)
            
            email_sent = await agentmail_service.send_demo_videos_email(
                to_email=user_email,
                product_name=demo['product_url'].split('//')[-1].split('/')[0],
                description=demo['description'],
                long_video_url=recorded_video_url,
                short_video_urls=short_video_urls
            )
            
            if email_sent:
                await self._update_demo_status(demo_id, DemoStatus.COMPLETED)
                logger.info(f"Demo {demo_id} completed successfully")
            else:
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message="Failed to send email"
                )
            
        except Exception as e:
            logger.error(f"Error processing demo {demo_id}: {str(e)}")
            await self._update_demo_status(
                demo_id,
                DemoStatus.FAILED,
                error_message=str(e)
            )
    
    async def _update_demo_status(
        self, 
        demo_id: str, 
        status: DemoStatus,
        error_message: Optional[str] = None
    ):
        """
        Update demo status in database
        """
        supabase = get_supabase_client()
        update_data = {"status": status.value}
        
        if error_message:
            update_data["error_message"] = error_message
        
        supabase.table("demos").update(update_data).eq("id", demo_id).execute()

video_generator = VideoGenerator()