from typing import Optional
from utils.supabase_client import get_supabase_client
from utils.config import settings
import logging
import os
import uuid
import tempfile
from pathlib import Path
from pydantic import HttpUrl, BaseModel, Field
from urllib.parse import urlparse

# Import recording module with advanced prompting
from services.recording import BrowserRecorder

# Dubbing dependencies
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
        
        # Initialize browser recorder with advanced prompting
        self.browser_recorder = BrowserRecorder(
            openai_api_key=self.openai_api_key,
            model="gpt-4o"
        )
        
    async def record_demo(self, demo_id: str, url: str, instruction: str, login_info: Optional[str] = None) -> Optional[str]:
        """
        Record a demo video of a website using browser automation with viral prompting
        Returns the URL of the recorded video
        """
        try:
            # Extract service name from URL for better prompting
            parsed_url = urlparse(url)
            service_name = parsed_url.hostname.replace('www.', '').split('.')[0] if parsed_url.hostname else "product"
            
            # Enhanced instructions with viral demo tips
            enhanced_instruction = f"""
{instruction}

Additional tips for viral demo:
- Start with curiosity and skepticism
- Show genuine surprise at impressive features
- Think out loud about how this solves real problems
- Build excitement throughout the demo
- End with clear value proposition
"""
            
            # Use BrowserRecorder with advanced prompting
            video_path = await self.browser_recorder.record_demo(
                demo_id=demo_id,
                website_url=url,
                service_name=service_name,
                instruction=enhanced_instruction,
                output_dir=None,  # Use temp directory
                headless=True
            )
            
            if not video_path:
                logger.error("Failed to record video")
                return None
            
            logger.info(f"Video recorded at: {video_path}")
            
            # Generate dubbing if enabled
            if self.enable_dubbing:
                video_path = await self._add_dubbing(video_path, url, instruction)
            
            # Upload to Supabase
            return await self._upload_video_to_storage(video_path)
            
        except Exception as e:
            logger.error(f"Recording error: {str(e)}")
            return None
    
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
            
            STYLE: Like a TOP tech influencer discovering an AMAZING product
            
            MUST INCLUDE:
            - HOOK in first 3 seconds ("Stop what you're doing!" / "This changes EVERYTHING!")
            - Talk directly to viewer ("YOU need to see this")
            - Build excitement progressively
            - Show genuine reactions ("Wait, WHAT?! It can do that?!")
            - Connect to real pain points ("If you've ever struggled with...")
            - Clear value propositions ("This literally saves hours")
            - Call to action at the end
            
            TONE:
            - Authentic and conversational
            - Excited but not overly salesy
            - Focus on problem-solving and value
            - Use natural pauses for emphasis
            
            Generate a SINGLE continuous transcript with:
            - Natural speech patterns
            - <break time="X.Xs" /> for dramatic pauses
            - Emphasis on key moments
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
            
            # Generate audio with engaging voice
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
            
            # Write output with optimized settings
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio_'+str(uuid.uuid4().hex)+'.m4a',
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
            file_extension = ".mp4" if video_path.endswith(".mp4") else ".webm"
            filename = f"demos/{uuid.uuid4()}/recording{file_extension}"
            
            # Upload to Supabase Storage
            supabase = get_supabase_client()
            supabase.storage.from_("demo-videos").upload(
                filename,
                video_data,
                file_options={"content-type": f"video/{file_extension[1:]}"}
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
