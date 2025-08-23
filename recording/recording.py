import asyncio
from browser_use import Agent, ChatOpenAI
from browser_use.browser.profile import BrowserProfile

from browser_use import BrowserSession, Agent
from dotenv import load_dotenv

load_dotenv()

# """

# You are an enthusiastic user who has just discovered an amazing website and you're genuinely excited to explore it. 
# Your goal is to naturally interact with the website while showcasing its most compelling features through authentic user behavior.
# Let's explore the "browser-use" website and find the hooking point of this website.

# 1. look around the landing page first. also show the pricing too.
# 2. go to product dashboard (cloud on top right) - if need login, use the account below
# 3. click one of sample requests.
# 4. let's see how the web agents works
# 5. wrap up the demo
# """

TASK_PROMPT = """
target website: https://browser-use.com/

click one button and click it. done.

ACCOUNT;
ID/EMAIL: junseong@bittersweet.ai
PASSWORD: vgm4zbr*ytj*EJY3anw
"""

async def main():

      browser_profile = BrowserProfile(
            headless=True,
            window_size={"width": 1920, "height": 1080},
            user_data_dir='~/.config/browseruse/profiles/default',
            record_video_dir='./data/recordings',
            record_video_size={"width": 1920, "height": 1080},
      )

      browser_session = BrowserSession(
         browser_profile=browser_profile,
      )

      await browser_session.start()

      agent = Agent(
         task=TASK_PROMPT,
         use_vision=True,
         vision_detail_level="low",
         llm=ChatOpenAI(model="o3"),
         browser_session=browser_session,
         browser_profile=browser_profile,
      )

      history = await agent.run()
      await browser_session.stop()


if __name__ == "__main__":
    asyncio.run(main())
