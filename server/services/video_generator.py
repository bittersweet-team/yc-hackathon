import asyncio
from typing import List, Optional
from models.demo import Demo, DemoStatus
from services.recording_service import recording_service
from services.klap_service import klap_service
from services.agentmail_service import agentmail_service
from utils.supabase_client import get_supabase_client
import logging
from models.klap_models import TaskObject, ExportObject, ExportStatus
import httpx

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
            
            # Send initial email notification
            logger.info(f"Sending initial notification to {user_email}")
            product_name = demo['product_url'].split('//')[-1].split('/')[0]
            
            await agentmail_service.send_demo_started_email(
                to_email=user_email,
                product_name=product_name,
                product_url=demo['product_url'],
                description=demo.get('description', '')
            )
            
            # Update status to recording
            await self._update_demo_status(demo_id, DemoStatus.RECORDING)
            
            # Step 1: Record the demo video
            logger.info(f"Recording demo for {demo['product_url']}")
            recorded_video_url = await recording_service.record_demo(
                demo['product_url'],
                demo['description']
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
            
            task_result: Optional[TaskObject] = await klap_service.submit_video_for_shorts(recorded_video_url)
            if not task_result:
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message="Failed to submit video to Klap"
                )
                return
            
            # Wait for Klap processing
            task_result: Optional[TaskObject] = await klap_service.wait_for_task_completion(task_result.id)
            if task_result.status != "ready":
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message=f"Klap processing failed: {task_result.error_message}"
                )
                return
            
            # Get generated shorts
            folder_id = task_result.output_id
            if task_result.output_type != "folder" or not folder_id:
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message="No folder ID returned from Klap"
                )
                return

            shorts = await klap_service.get_projects(folder_id)
            if not shorts:
                await self._update_demo_status(
                    demo_id,
                    DemoStatus.FAILED,
                    error_message="No shorts generated"
                )
                return
            
            # Export top shorts (up to 3)
            short_video_urls = []
            top_shorts = sorted(shorts, key=lambda x: x.virality_score, reverse=True)[:3]
            
            for i, short in enumerate(top_shorts):
                project_id = short.id
                if not project_id:
                    continue

                export_result: Optional[ExportObject] = await klap_service.create_export(folder_id, project_id)
                if not export_result:
                    continue

                export_result: Optional[ExportObject] = await klap_service.wait_for_export_completion(export_result)
                if export_result.status != ExportStatus.READY or not export_result.src_url:
                    continue

                # Download video from Klap and upload to Supabase
                supabase_url = await self._upload_video_to_supabase(
                    video_url=str(export_result.src_url),
                    demo_id=demo_id,
                    video_type=f"short_{i+1}"
                )
                
                if supabase_url:
                    short_video_urls.append(supabase_url)
                else:
                    # Fallback to Klap URL if upload fails
                    logger.warning(f"Failed to upload short {i+1} to Supabase, using Klap URL")
                    short_video_urls.append(str(export_result.src_url))

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

    async def _upload_video_to_supabase(
        self,
        video_url: str,
        demo_id: str,
        video_type: str = "video"
    ) -> Optional[str]:
        """
        Download video from URL and upload to Supabase storage
        Returns the public URL of the uploaded video
        """
        try:
            # Download video from Klap
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(video_url)
                response.raise_for_status()
                video_data = response.content
            
            # Generate filename with same structure as recording service
            # demos/{uuid}/{type}.mp4
            filename = f"demos/{demo_id}/{video_type}.mp4"
            
            # Upload to Supabase Storage
            supabase = get_supabase_client()
            
            # Check if file already exists and delete it
            try:
                existing = supabase.storage.from_("demo-videos").list(f"demos/{demo_id}")
                if existing and any(f.get('name') == f"{video_type}.mp4" for f in existing):
                    supabase.storage.from_("demo-videos").remove([filename])
            except:
                pass  # Ignore errors when checking/deleting existing files
            
            # Upload the new video
            response = supabase.storage.from_("demo-videos").upload(
                filename,
                video_data,
                file_options={"content-type": "video/mp4", "upsert": "true"}
            )
            
            # Get public URL
            public_url = supabase.storage.from_("demo-videos").get_public_url(filename)
            
            logger.info(f"Video uploaded to Supabase: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload video to Supabase: {str(e)}")
            return None

video_generator = VideoGenerator()
