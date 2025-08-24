#!/usr/bin/env python3
"""
Apply AI-generated dubbing to video using ElevenLabs TTS
Creates a dubbed version of your video with synchronized narration
"""

import json
import os
import sys
import argparse
import tempfile
from pathlib import Path
from typing import Dict
import asyncio
import uuid
from dotenv import load_dotenv

from elevenlabs.client import AsyncElevenLabs
from loguru import logger

from moviepy import VideoFileClip, AudioFileClip


load_dotenv()



class VideoDubbingProcessor:
    """Process video with AI-generated dubbing"""
    
    def __init__(self, api_key: str, voice_id: str, model: str = "eleven_monolingual_v1"):
        """Initialize with ElevenLabs API"""
        self.client = AsyncElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.model = model
        
    def load_script(self, script_path: str) -> str:
        """Load dubbing script from JSON"""
        with open(script_path, 'r') as f:
            data = json.load(f)
        return data.get('transcript', data)
    
    async def generate_speech(self, text: str, output_path: str) -> str:
        """Generate speech for the complete transcript"""
        logger.info(f"  🎙️ Generating audio for transcript ({len(text)} characters)...")
        
        try:
            # Generate audio (returns async generator)
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model,
                output_format="mp3_44100_128",
            )
            
            # Collect audio chunks from async generator
            audio_chunks = []
            async for chunk in audio_generator:
                audio_chunks.append(chunk)
            
            # Save audio to file
            with open(output_path, 'wb') as f:
                for chunk in audio_chunks:
                    f.write(chunk)
            
            return output_path
            
        except Exception as e:
            logger.info(f"  ❌ Error generating audio: {str(e)}")
            return None
    
    
    async def create_dubbed_audio(self, transcript: str, temp_dir: str) -> str:
        """Create dubbed audio from transcript"""
        logger.info("\n🎬 Creating dubbed audio track...")
        
        # Generate single audio file
        output_path = os.path.join(temp_dir, "dubbed_audio.mp3")
        result = await self.generate_speech(transcript, output_path)
        
        if result and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            logger.info(f"  ✅ Audio track created: {os.path.getsize(output_path) / 1024:.1f} KB")
            return output_path
        else:
            logger.info("  ❌ Failed to create valid audio track")
            return None
    
    
    def apply_dubbing_to_video(self, video_path: str, audio_path: str, output_path: str):
        """Apply dubbed audio to video"""
        logger.info("🎞️ Applying dubbing to video...")
        
        # Load video
        video = VideoFileClip(video_path)
        
        # Load dubbed audio
        dubbed_audio = AudioFileClip(audio_path)
        
        # Set audio to video (replace original audio completely)
        final_video = video.with_audio(dubbed_audio)
        
        # Write output
        logger.info(f"  💾 Saving to: {output_path}")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio_'+str(uuid.uuid4().hex)+'.m4a',
            remove_temp=True,
            logger=None  # Suppress moviepy output
        )
        
        # Cleanup
        video.close()
        dubbed_audio.close()
        final_video.close()
        
        logger.info(f"\n✅ Dubbed video saved to: {output_path}")
    
    async def process_video(self, video_path: str, script_path: str, output_path: str):
        """Complete dubbing process with async"""
        # Load script
        transcript = self.load_script(script_path)
        logger.info(f"\n📝 Loaded transcript ({len(transcript)} characters)")
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate dubbed audio (async)
            dubbed_audio_path = await self.create_dubbed_audio(
                transcript, temp_dir
            )
            
            if dubbed_audio_path is None:
                logger.info("\n❌ Failed to generate audio track. Please check:")
                logger.info("  1. Your ElevenLabs API key is valid")
                logger.info("  2. You have sufficient API credits")
                logger.info("  3. The transcript is not empty")
                return
            
            # Apply to video
            self.apply_dubbing_to_video(
                video_path, dubbed_audio_path, output_path
            )


async def async_main():
    parser = argparse.ArgumentParser(
        description="Apply AI-generated dubbing to video using ElevenLabs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python apply_dubbing.py video.mp4 script.json
  python apply_dubbing.py video.mp4 script.json --voice josh
  python apply_dubbing.py video.mp4 script.json --no-original
  python apply_dubbing.py video.mp4 script.json --original-volume 0.1
  
Available voices:
  rachel, domi, bella, antoni, elli, josh, adam, arnold, sam, glinda
        """
    )
    
    parser.add_argument("--video", help="Path to video file")
    parser.add_argument("--script", help="Path to dubbing script JSON")
    
    parser.add_argument(
        "--output", "-o",
        help="Output video path (default: video_dubbed.mp4)",
        default=None
    )
    
    parser.add_argument(
        "--voice", "-v",
        help="ElevenLabs voice to use (default: bella)",
        default="1SM7GgM6IMuvQlz2BwM3",
    )
    
    parser.add_argument(
        "--model", "-m",
        help="ElevenLabs model (default: eleven_monolingual_v1)",
        default="eleven_v3",
    )
    
    parser.add_argument(
        "--api-key", "-k",
        help="ElevenLabs API key (or set ELEVENLABS_API_KEY env var)",
        default=None
    )
    
    
    parser.add_argument(
        "--voice-id",
        help="Custom ElevenLabs voice ID (overrides --voice)",
        default=None
    )
    
    args = parser.parse_args()
    
    # Validate files
    if not os.path.exists(args.video):
        logger.info(f"Error: Video file not found: {args.video}")
        sys.exit(1)
    
    if not os.path.exists(args.script):
        logger.info(f"Error: Script file not found: {args.script}")
        sys.exit(1)
    
    # Get API key
    api_key = args.api_key or os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.info("Error: Please provide ElevenLabs API key")
        logger.info("  --api-key YOUR_KEY")
        logger.info("  or set ELEVENLABS_API_KEY environment variable")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        video_name = Path(args.video).stem
        output_path = f"{video_name}_dubbed.mp4"
    
    # Process video
    try:
        processor = VideoDubbingProcessor(
            api_key=api_key,
            voice_id=args.voice_id,
            model=args.model
        )
        
        await processor.process_video(
            video_path=args.video,
            script_path=args.script,
            output_path=output_path
        )
        
        logger.info(f"\n🎉 Success! Dubbed video created: {output_path}")
        
    except Exception as e:
        logger.info(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point that runs the async main"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
