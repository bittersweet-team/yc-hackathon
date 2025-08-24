#!/usr/bin/env python3
"""
Generate viral dubbing script from video using Google Gemini AI

This script creates influencer-style dubbing scripts with timestamps
for any video file, perfect for creating viral content.
"""

import json
import sys
import os
import argparse
from datetime import datetime
import time

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")


class ViralDubbingScript(BaseModel):
    transcript: str = Field(description="Complete dubbing transcript with SSML break tags")


def generate_viral_dubbing(video_path: str, api_key: str, model_name: str = "gemini-2.0-pro", temperature: float = 0.9, style: str = "influencer", verbose: bool = False) -> dict:
    """Generate viral dubbing script from video"""
    
    logger.info(f"Starting dubbing generation for video: {video_path}")
    logger.debug(f"Parameters: model={model_name}, temp={temperature}, style={style}")
    
    # Configure Gemini
    logger.info("Initializing Gemini client")
    client = genai.Client(api_key=api_key)
    
    if verbose:
        print(f"📊 Using model: {model_name}")
        print(f"🌡️ Temperature: {temperature}")
    
    # Upload video
    video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    logger.info(f"Uploading video: {os.path.basename(video_path)} ({video_size_mb:.2f} MB)")
    print(f"📤 Uploading video: {video_path}")
    
    upload_start = time.time()
    video_file = client.files.upload(file=video_path)
    upload_time = time.time() - upload_start
    
    logger.success(f"Video uploaded successfully in {upload_time:.2f} seconds")
    logger.debug(f"Video URI: {video_file.uri}")
    print("✅ Video uploaded!")
    
    # Style-specific prompts
    style_prompts = {
        "influencer": "Like a TOP influencer introducing an AMAZING product",
        "tech_reviewer": "Like MKBHD or Marques Brownlee reviewing cutting-edge tech",
        "hype": "Maximum energy like a hypebeast unveiling the hottest drop",
        "educational": "Engaging educator making complex things simple and exciting",
        "dramatic": "Movie trailer narrator building epic suspense and revelation"
    }
    
    # Generate viral script
    selected_style = style_prompts.get(style, style_prompts["influencer"])
    logger.info(f"Using style: {style} - {selected_style}")
    
    prompt = f"""
    Create a VIRAL dubbing script for this video. IGNORE any white/blank screen at the beginning.
    
    STYLE: {selected_style}
    
    MUST INCLUDE:
    - HOOK in first 3 seconds ("OMG, you won't believe this..." / "Stop scrolling RIGHT NOW!")
    - Talk directly to viewer ("YOU need this", "Trust me")
    - Intro what this product is and how can it help you
    - Show off the BEST features dramatically
    
    Make it sound like:
    - Influencer sharing their new obsession
    - Someone who genuinely can't contain their excitement
    
    IMPORTANT:
    - Generate a SINGLE continuous transcript
    - Use breaks to create natural pauses and timing - X.X seconds break using <break time=“X.Xs” /> between major points
    - Start speaking right away (no break at the beginning)
    - Every line should make viewers more excited!
    - Focus on the most ATTRACTIVE and IMPRESSIVE aspects
    - Sync with video timing
    """
    
    logger.info(f"Sending request to Gemini model: {model_name}")
    logger.debug(f"Prompt length: {len(prompt)} characters")
    
    generation_start = time.time()
    try:
        response = client.models.generate_content(
            contents=types.Content(parts=[
                types.Part(
                    file_data=types.FileData(file_uri=video_file.uri, mime_type="video/webm"),
                    video_metadata=types.VideoMetadata(fps=2),
                ),
                types.Part(text=prompt),
            ]),
            model=model_name,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ViralDubbingScript,
            ),
        )
        generation_time = time.time() - generation_start
        logger.success(f"Generated script in {generation_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Failed to generate content: {str(e)}")
        raise
    
    # Parse response
    logger.info("Parsing response to structured format")
    script = response.parsed
    
    # Post-process to fix SSML break tag quotes
    # Replace escaped quotes in break tags with regular quotes
    script.transcript = script.transcript.replace('<break time="', '<break time=“')
    script.transcript = script.transcript.replace('" />', '” />')
    
    # Log script details
    transcript_length = len(script.transcript)
    break_count = script.transcript.count('<break')
    logger.info(f"Generated transcript with {transcript_length} characters and {break_count} breaks")
    
    return script.model_dump()


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate viral dubbing script from video using Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_dubbing.py video.mp4
  python generate_dubbing.py video.mp4 --output custom_script.json
  python generate_dubbing.py video.mp4 --model gemini-1.5-flash
  python generate_dubbing.py video.mp4 --temperature 0.7
        """
    )
    
    parser.add_argument(
        "video",
        help="Path to the video file"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: dubbing_script_TIMESTAMP.json)",
        default=None
    )
    
    parser.add_argument(
        "--model", "-m",
        help="Gemini model to use (default: gemini-2.0-pro)",
        default="gemini-2.5-pro",
    )
    
    parser.add_argument(
        "--temperature", "-t",
        help="Temperature for generation (0.0-1.0, default: 0.9)",
        type=float,
        default=0.9
    )
    
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API key (can also use GEMINI_API_KEY env var)",
        default=None
    )
    
    parser.add_argument(
        "--verbose", "-v",
        help="Show detailed output",
        action="store_true"
    )
    
    parser.add_argument(
        "--style",
        help="Style of dubbing (default: influencer)",
        default="influencer",
        choices=["influencer", "tech_reviewer", "hype", "educational", "dramatic"]
    )
    
    parser.add_argument(
        "--no-emoji",
        help="Disable emojis in output",
        action="store_true"
    )
    
    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>")
        logger.debug("Debug mode enabled")
    
    # Validate video file
    if not os.path.exists(args.video):
        logger.error(f"Video file not found: {args.video}")
        print(f"Error: Video file not found: {args.video}")
        sys.exit(1)
    
    logger.info(f"Input video: {args.video}")
    
    # Get API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("No API key provided")
        print("Error: Please provide API key via --api-key or set GEMINI_API_KEY environment variable")
        print("export GEMINI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    logger.info("API key configured")
    
    try:
        if args.verbose:
            print(f"\n📹 Processing video: {args.video}")
            print(f"📁 Video size: {os.path.getsize(args.video) / 1024 / 1024:.2f} MB")
        
        print("\n🚀 Generating VIRAL dubbing script...")
        
        # Generate script
        logger.info("Starting script generation")
        generation_start = time.time()
        
        script = generate_viral_dubbing(
            args.video, 
            api_key,
            model_name=args.model,
            temperature=args.temperature,
            style=args.style,
            verbose=args.verbose
        )
        
        total_time = time.time() - generation_start
        logger.success(f"Complete pipeline finished in {total_time:.2f} seconds")
        
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"dubbing_script_{timestamp}.json"
        
        logger.info(f"Saving script to: {output_file}")
        with open(output_file, 'w') as f:
            json.dump(script, f, indent=2)
        logger.success(f"Script saved successfully")
        
        # Print script
        if not args.no_emoji:
            print("\n" + "="*60)
            print("🎬 VIRAL DUBBING SCRIPT")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("VIRAL DUBBING SCRIPT")
            print("="*60)
        
        print(f"\nTranscript:")
        print("-" * 60)
        print(script['transcript'])
        
        print("\n" + "="*60)
        
        if not args.no_emoji:
            print(f"\n✅ Script saved to: {output_file}")
        else:
            print(f"\nScript saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Script generation failed: {str(e)}")
        logger.exception("Full error traceback:")
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
