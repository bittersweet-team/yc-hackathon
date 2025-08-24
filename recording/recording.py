import asyncio
from browser_use import Agent, ChatOpenAI
from browser_use.browser.profile import BrowserProfile

from browser_use import BrowserSession, Agent
from dotenv import load_dotenv

load_dotenv()

INSTRUCTION_FROM_USER = """
# 1. look around the landing page first. also show the pricing too.
# 2. go to product dashboard (cloud on top right) - if need login, use the account below
# 3. click one of sample requests.
# 4. let's see how the web agents works
# 5. wrap up the demo
"""

LOGIN_INFO = """
ACCOUNT;
ID/EMAIL: junseong@bittersweet.ai
PASSWORD: vgm4zbr*ytj*EJY3anw
"""

SERVICE_NAME = "browser-use"
WEBSITE_URL = "https://browser-use.com/"


TASK_PROMPT = """
target website: {WEBSITE_URL}

You are Alex, a tech-savvy product manager at a fast-growing startup who's been struggling with repetitive web tasks and browser automation. 
You just discovered {SERVICE_NAME} through a colleague's recommendation and you're genuinely excited to see if this could solve your workflow problems.

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
{INSTRUCTION_FROM_USER}

## Account credentials for dashboard access -> Strictly follow these credentials
{LOGIN_INFO}

Remember: This is for a demo video that needs to go viral. Be authentic, show genuine reactions, and focus on the most impressive and unique features. Don't just click around - tell a story that hooks viewers from the first second!
"""   

async def main():

      browser_profile = BrowserProfile(
            headless=True,
            window_size={"width": 1920, "height": 1080},
            user_data_dir='~/.config/browseruse/profiles/default',
            record_video_dir='./data/recordings',
            record_video_size={"width": 1920, "height": 1080},
            highlight_elements=False,
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
