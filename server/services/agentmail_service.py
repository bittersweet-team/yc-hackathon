import httpx
from typing import List, Optional, Dict
from utils.config import settings
import logging

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
            subject = f"Demo Generation Started for {product_name}"
            
            # Create HTML email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">🚀 Your Demo is Being Generated!</h2>
                
                <p>Hi there,</p>
                
                <p>We've started generating demo videos for <strong>{product_name}</strong>.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Product URL:</strong><br><a href="{product_url}" style="color: #007bff;">{product_url}</a></p>
                    {f'<p><strong>Description:</strong><br>{description}</p>' if description else ''}
                </div>
                
                <h3 style="color: #555;">⏱️ What's Happening Now:</h3>
                <ol style="line-height: 1.8;">
                    <li>Recording your product demo</li>
                    <li>Processing the video with AI</li>
                    <li>Generating optimized short-form clips</li>
                    <li>Preparing your final videos</li>
                </ol>
                
                <p style="background-color: #e8f4f8; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                    <strong>⏰ Estimated Time:</strong> 5-10 minutes<br>
                    We'll send you another email once your videos are ready!
                </p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 14px;">
                        You're receiving this email because you requested a demo generation.
                        If you didn't request this, please ignore this email.
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
