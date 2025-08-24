import asyncio
from browser_use import Agent, ChatOpenAI
from browser_use.browser.profile import BrowserProfile
from browser_use import BrowserSession
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

class BrowserRecorder:
    """Advanced browser recording with viral demo prompting"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o"):
        self.openai_api_key = openai_api_key
        self.model = model
    
    def create_viral_task_prompt(self, 
                                website_url: str, 
                                service_name: str,
                                instruction: str
      ) -> str:
        """
        Create an advanced task prompt for viral demo recording
        """
        return f"""
target website: {website_url}

You are Alex, a tech-savvy product manager at a fast-growing startup who's been struggling with repetitive web tasks and browser automation. 
You just discovered {service_name} through a colleague's recommendation and you're genuinely excited to see if this could solve your workflow problems.

Your persona:
- You're looking for something that "just works" without writing complex code
- You appreciate good UX and get excited about innovative features
- You think out loud as you explore, sharing genuine reactions and insights
- You're the type who loves finding hidden gems in products

Demo objectives (for viral video):
1. Create "wow moments" by discovering key features naturally
2. Show genuine excitement when finding powerful capabilities
3. Demonstrate real use cases that viewers can relate to
4. Build tension and payoff - start skeptical, become amazed
5. Focus on the "magic" - what makes this different from everything else
6. Make viewers think "I need this RIGHT NOW"

Exploration approach:
- Start with healthy skepticism: "Another automation tool? Let's see what makes this special..."
- React authentically to impressive features: "Wait, it can do THAT?"
- Connect features to real problems: "This would save me hours every week!"
- Show the "aha moment" when you realize the true potential
- End with enthusiasm: "This changes everything for our team!"

## User's specific instructions for demo flow -> Strictly follow these instructions
{instruction}

## Account credentials for dashboard access -> Strictly follow these credentials
ID/EMAIL: junseong@bittersweet.ai
PASSWORD: vgm4zbr*ytj*EJY3anw

Remember: This is for a demo video that needs to go viral. Be authentic, show genuine reactions, and focus on the most impressive and unique features. Don't just click around - tell a story that hooks viewers from the first second!
"""
    
    async def record_demo(self,
                         website_url: str,
                         service_name: str,
                         instruction: str,
                         output_dir: Optional[str] = None,
                         headless: bool = True) -> Optional[str]:
        """
        Record a demo video with advanced prompting
        
        Args:
            website_url: Target website URL
            service_name: Name of the service being demoed
            instruction: Specific instructions for the demo
            output_dir: Directory to save the recording (temp if not specified)
            headless: Run browser in headless mode
            
        Returns:
            Path to the recorded video file or None if failed
        """
        try:
            # Create output directory
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="demo_recording_")
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Recording to directory: {output_dir}")
            
            # Configure browser profile for recording
            browser_profile = BrowserProfile(
                headless=headless,
                window_size={"width": 1920, "height": 1080},
                user_data_dir=os.path.join(output_dir, 'browser_profile'),
                record_video_dir=output_dir,
                record_video_size={"width": 1920, "height": 1080},
                highlight_elements=False,
                disable_security=True,
            )
            
            # Create browser session
            browser_session = BrowserSession(browser_profile=browser_profile)
            await browser_session.start()
            
            # Create viral task prompt
            task_prompt = self.create_viral_task_prompt(
                website_url=website_url,
                service_name=service_name,
                instruction=instruction
            )
            
            # Create and configure agent
            agent = Agent(
                task=task_prompt,
                use_vision=True,
                vision_detail_level="low",
                llm=ChatOpenAI(model=self.model, api_key=self.openai_api_key),
                browser_session=browser_session,
                browser_profile=browser_profile,
            )
            
            # Run the recording
            logger.info(f"Starting viral demo recording for {website_url}")
            await agent.run()
            await browser_session.stop()
            
            # Find the recorded video file
            video_files = list(Path(output_dir).glob("*.webm"))
            if not video_files:
                logger.error("No video file found after recording")
                return None
            
            video_path = str(video_files[0])
            logger.info(f"Demo video recorded successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Recording failed: {str(e)}")
            return None


# Standalone execution for testing
async def main():
    """Example usage for standalone testing"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Example configuration
    INSTRUCTION = """
# 1. Look around the landing page first. Also show the pricing too.
# 2. Go to product dashboard (cloud on top right) - if need login, use the account below
# 3. Click one of sample requests.
# 4. Let's see how the web agents works
# 5. Wrap up the demo
"""
    
    LOGIN_INFO = """
ACCOUNT:
ID/EMAIL: demo@example.com
PASSWORD: demo123
"""
    
    recorder = BrowserRecorder(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    video_path = await recorder.record_demo(
        website_url="https://browser-use.com/",
        service_name="browser-use",
        instruction=INSTRUCTION,
        login_info=LOGIN_INFO,
        output_dir="./data/recordings",
        headless=True
    )
    
    if video_path:
        print(f"Recording saved to: {video_path}")
    else:
        print("Recording failed")


if __name__ == "__main__":
    asyncio.run(main())
