import httpx
from typing import List, Optional, Dict
from utils.config import settings
import logging

logger = logging.getLogger(__name__)

class AgentMailService:
    def __init__(self):
        self.api_key = settings.agentmail_api_key
        self.base_url = "https://api.agentmail.to"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_inbox(self, domain: Optional[str] = None) -> Dict:
        """
        Create a new inbox for sending emails
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {}
                if domain:
                    payload["domain"] = domain
                    
                response = await client.post(
                    f"{self.base_url}/inboxes",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Failed to create inbox: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"AgentMail inbox creation error: {str(e)}")
            return None
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email with optional attachments
        """
        try:
            # Create inbox if from_email not specified
            if not from_email:
                inbox = await self.create_inbox()
                if inbox:
                    from_email = inbox.get("email", "noreply@agentmail.to")
                else:
                    from_email = "noreply@agentmail.to"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "from": from_email,
                    "to": to_email,
                    "subject": subject,
                    "body": body,
                    "html": True
                }
                
                if attachments:
                    payload["attachments"] = attachments
                
                response = await client.post(
                    f"{self.base_url}/messages/send",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
                else:
                    logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"AgentMail send error: {str(e)}")
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
            subject = f"Your {product_name} Demo Videos Are Ready!"
            
            # Create HTML email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">🎥 Your Demo Videos Are Ready!</h2>
                
                <p>Hi there,</p>
                
                <p>Great news! We've successfully generated demo videos for <strong>{product_name}</strong>.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Product Description:</strong><br>{description}</p>
                </div>
                
                <h3 style="color: #555;">📹 Full Demo Video</h3>
                <p>Watch the complete product demo:</p>
                <a href="{long_video_url}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">View Full Demo</a>
                
                <h3 style="color: #555; margin-top: 30px;">🎬 Short-Form Videos</h3>
                <p>Perfect for social media sharing:</p>
                <ul>
            """
            
            for i, url in enumerate(short_video_urls, 1):
                body += f"""
                    <li style="margin: 10px 0;">
                        <a href="{url}" style="color: #007bff;">Short Video #{i}</a>
                    </li>
                """
            
            body += """
                </ul>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 14px;">
                        These videos were automatically generated using AI technology. 
                        Feel free to download and share them!
                    </p>
                </div>
                
                <p style="margin-top: 20px;">
                    Best regards,<br>
                    <strong>Demo Hunters Team</strong>
                </p>
            </body>
            </html>
            """
            
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=body
            )
            
        except Exception as e:
            logger.error(f"Failed to send demo videos email: {str(e)}")
            return False

agentmail_service = AgentMailService()