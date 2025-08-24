import httpx
from typing import List, Optional, Dict
from utils.config import settings
import logging
from services.email_templates import get_demo_started_email_html, get_demo_complete_email_html

from agentmail import AgentMail

logger = logging.getLogger(__name__)

class AgentMailService:
    def __init__(self):
        self.agentmail = AgentMail(api_key=settings.agentmail_api_key)
    
    async def create_inbox(self, domain: Optional[str] = None) -> Dict:
        """
        Create a new inbox for sending emails
        """
        try:
            return self.agentmail.inboxes.create(domain=domain)
        except Exception as e:
            logger.error(f"AgentMail inbox creation error: {str(e)}")
            return None
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str,
        *,
        from_email: str = "demo-hunters@agentmail.to"
    ) -> bool:
        """
        Send an email with optional attachments
        """
        try:
            self.agentmail.inboxes.messages.send(
                inbox_id=from_email,
                to=[to_email],
                subject=subject,
                html=body
            )
            return True                    
        except Exception as e:
            logger.error(f"AgentMail send error: {str(e)}")
            return False

    async def send_demo_started_email(
        self,
        to_email: str,
        product_name: str,
        product_url: str,
        description: str
    ) -> bool:
        """
        Send email notification when demo processing starts
        """
        try:
            subject = f"Demo Generation Started for {product_name} 🚀"
            
            # Use the new email template
            body = get_demo_started_email_html(product_name, product_url, description)
            
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=body
            )
            
        except Exception as e:
            logger.error(f"Failed to send demo started email: {str(e)}")
            return False
    
    async def send_demo_videos_email(
        self,
        to_email: str,
        product_name: str,
        description: str,
        long_video_url: str,
        short_video_urls: List[str]
    ) -> bool:
        """
        Send demo videos to user via email
        """
        try:
            subject = f"Your {product_name} Demo Videos Are Ready! 🎬"
            
            # Use the new email template
            body = get_demo_complete_email_html(product_name, description, long_video_url, short_video_urls)
            
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=body
            )
            
        except Exception as e:
            logger.error(f"Failed to send demo videos email: {str(e)}")
            return False

agentmail_service = AgentMailService()
