from typing import Optional
from utils.supabase_client import get_supabase_client
from utils.config import settings
import logging
import os
import uuid
import tempfile
from pathlib import Path
from pydantic import HttpUrl, BaseModel, Field

# Recording dependencies
from browser_use import Agent, ChatOpenAI
from browser_use.browser.profile import BrowserProfile
from browser_use import BrowserSession
from google import genai
from google.genai import types
from elevenlabs.client import AsyncElevenLabs
from moviepy import VideoFileClip, AudioFileClip

logger = logging.getLogger(__name__)

class ViralDubbingScript(BaseModel):
    transcript: str = Field(description="Complete dubbing transcript with SSML break tags")

class RecordingService:
    def __init__(self):
        # Initialize API keys from settings
        self.openai_api_key = settings.openai_api_key
        self.gemini_api_key = settings.gemini_api_key
        self.elevenlabs_api_key = settings.elevenlabs_api_key
        self.elevenlabs_voice_id = settings.elevenlabs_voice_id
        self.enable_dubbing = settings.enable_dubbing
        
    async def record_demo(self, url: str, instruction: str) -> Optional[str]:
        """
        Record a demo video of a website using browser automation
        Returns the URL of the recorded video
        """
        try:
            # Create temp directory for recordings
            temp_dir = tempfile.mkdtemp(prefix="demo_recording_")
            
            # Configure browser profile for recording
            browser_profile = BrowserProfile(
                headless=True,
                window_size={"width": 1920, "height": 1080},
                user_data_dir=os.path.join(temp_dir, 'browser_profile'),
                record_video_dir=temp_dir,
                record_video_size={"width": 1920, "height": 1080},
                highlight_elements=False,
            )
            
            # Create browser session
            browser_session = BrowserSession(browser_profile=browser_profile)
            await browser_session.start()
            
            # Create task prompt
            task_prompt = self._create_task_prompt(url, instruction)
            
            # Create and run agent
            agent = Agent(
                task=task_prompt,
                use_vision=True,
                vision_detail_level="low",
                llm=ChatOpenAI(model="gpt-4o", api_key=self.openai_api_key),
                browser_session=browser_session,
                browser_profile=browser_profile,
            )
            
            # Run the recording
            logger.info(f"Starting browser recording for {url}...")
            await agent.run()
            await browser_session.stop()
            
            # Find the recorded video file
            video_files = list(Path(temp_dir).glob("*.webm"))
            if not video_files:
                logger.error("No video file found after recording")
                return None
            
            video_path = str(video_files[0])
            logger.info(f"Video recorded at: {video_path}")
            
            # Generate dubbing if enabled
            if self.enable_dubbing:
                video_path = await self._add_dubbing(video_path, url, instruction)
            
            # Upload to Supabase
            return await self._upload_video_to_storage(video_path)
            
        except Exception as e:
            logger.error(f"Recording error: {str(e)}")
            return None
    
    def _create_task_prompt(self, url: str, instruction: str) -> str:
        """
        Create a task prompt for the browser agent
        """
        return f"""
        Target website: {url}
        
        You are Alex, a tech-savvy product manager exploring this product.
        
        Demo objectives:
        1. Show the main features naturally
        2. Demonstrate real use cases
        3. Focus on what makes this product unique
        
        User's specific instructions:
        {instruction}
        
        Be authentic and show genuine reactions to features you discover.
        """
    
    async def _add_dubbing(self, video_path: str, url: str, instruction: str) -> str:
        """
        Add AI-generated dubbing to the recorded video
        """
        try:
            logger.info("Generating dubbing script...")
            
            # Generate dubbing script
            script = await self._generate_dubbing_script(video_path, url, instruction)
            if not script:
                logger.warning("Failed to generate dubbing script, returning original video")
                return video_path
            
            # Generate audio from script
            audio_path = await self._generate_audio(script)
            if not audio_path:
                logger.warning("Failed to generate audio, returning original video")
                return video_path
            
            # Apply dubbing to video
            output_path = video_path.replace('.webm', '_dubbed.mp4')
            self._apply_dubbing_to_video(video_path, audio_path, output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Dubbing error: {str(e)}")
            return video_path
    
    async def _generate_dubbing_script(self, video_path: str, url: str, instruction: str) -> Optional[str]:
        """
        Generate a viral dubbing script using Gemini
        """
        try:
            client = genai.Client(api_key=self.gemini_api_key)
            
            # Upload video to Gemini
            video_file = client.files.upload(file=video_path)
            
            prompt = f"""
            Create a VIRAL dubbing script for this demo video of {url}.
            
            The demo was created with these instructions: {instruction}
            
            STYLE: Like a TOP influencer introducing an AMAZING product
            
            MUST INCLUDE:
            - HOOK in first 3 seconds
            - Talk directly to viewer
            - Show off the BEST features dramatically
            - Generate a SINGLE continuous transcript
            - Use <break time="X.Xs" /> for natural pauses
            """
            
            response = client.models.generate_content(
                contents=types.Content(parts=[
                    types.Part(
                        file_data=types.FileData(file_uri=video_file.uri, mime_type="video/webm"),
                        video_metadata=types.VideoMetadata(fps=2),
                    ),
                    types.Part(text=prompt),
                ]),
                model="gemini-2.5-pro",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ViralDubbingScript,
                ),
            )
            
            script = response.parsed
            return script.transcript
            
        except Exception as e:
            logger.error(f"Script generation error: {str(e)}")
            return None
    
    async def _generate_audio(self, transcript: str) -> Optional[str]:
        """
        Generate audio from transcript using ElevenLabs
        """
        try:
            client = AsyncElevenLabs(api_key=self.elevenlabs_api_key)
            
            # Generate audio
            audio_generator = client.text_to_speech.convert(
                text=transcript,
                voice_id=self.elevenlabs_voice_id,
                model_id="eleven_v3",
                output_format="mp3_44100_128",
            )
            
            # Collect audio chunks
            audio_chunks = []
            async for chunk in audio_generator:
                audio_chunks.append(chunk)
            
            # Save to temp file
            temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            for chunk in audio_chunks:
                temp_audio.write(chunk)
            temp_audio.close()
            
            return temp_audio.name
            
        except Exception as e:
            logger.error(f"Audio generation error: {str(e)}")
            return None
    
    def _apply_dubbing_to_video(self, video_path: str, audio_path: str, output_path: str):
        """
        Apply dubbed audio to video using moviepy
        """
        try:
            video = VideoFileClip(video_path)
            dubbed_audio = AudioFileClip(audio_path)
            
            # Replace original audio with dubbed audio
            final_video = video.with_audio(dubbed_audio)
            
            # Write output
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None
            )
            
            # Cleanup
            video.close()
            dubbed_audio.close()
            final_video.close()
            
            logger.info(f"Dubbed video created: {output_path}")
            
        except Exception as e:
            logger.error(f"Video dubbing error: {str(e)}")
            raise
    
    async def _upload_video_to_storage(self, video_path: str) -> Optional[str]:
        """
        Upload video to Supabase Storage
        """
        try:
            with open(video_path, "rb") as f:
                video_data = f.read()
            
            # Generate unique filename
            filename = f"demos/{uuid.uuid4()}/recording.mp4"
            
            # Upload to Supabase Storage
            supabase = get_supabase_client()
            supabase.storage.from_("demo-videos").upload(
                filename,
                video_data,
                file_options={"content-type": "video/mp4"}
            )
            
            # Get public URL
            public_url: HttpUrl = supabase.storage.from_("demo-videos").get_public_url(filename)
            
            logger.info(f"Video uploaded to: {public_url}")
            return str(public_url)
            
        except Exception as e:
            logger.error(f"Failed to upload video: {str(e)}")
            return None
    
    async def check_recording_status(self, recording_id: str) -> dict:
        """
        Check the status of a recording job
        For integrated recording, always returns completed
        """
        # recording_id kept for API compatibility
        return {"status": "completed", "message": "Recording completed"}

recording_service = RecordingService()
