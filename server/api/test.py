from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.recording_service import recording_service
from services.klap_service import klap_service
from services.agentmail_service import agentmail_service
import logging

router = APIRouter(prefix="/api/test", tags=["testing"])
logger = logging.getLogger(__name__)

class TestResponse(BaseModel):
    success: bool
    message: str
    data: dict = {}

@router.post("/recording", response_model=TestResponse)
async def test_recording():
    """
    Test recording service with mock video
    """
    try:
        video_url = await recording_service.record_demo("https://example.com")
        
        if video_url:
            return TestResponse(
                success=True,
                message="Mock recording successful",
                data={"video_url": video_url}
            )
        else:
            return TestResponse(
                success=False,
                message="Recording failed",
                data={}
            )
    except Exception as e:
        logger.error(f"Test recording error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/klap", response_model=TestResponse)
async def test_klap(video_url: str):
    """
    Test Klap API with a video URL
    """
    try:
        # Submit to Klap
        task_id = await klap_service.submit_video_for_shorts(
            video_url,
            "Test video for API testing"
        )
        
        if task_id:
            # Check status (don't wait for completion in API call)
            status = await klap_service.check_task_status(task_id)
            
            return TestResponse(
                success=True,
                message="Video submitted to Klap",
                data={
                    "task_id": task_id,
                    "status": status
                }
            )
        else:
            return TestResponse(
                success=False,
                message="Failed to submit to Klap",
                data={}
            )
    except Exception as e:
        logger.error(f"Test Klap error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agentmail", response_model=TestResponse)
async def test_agentmail(email: str):
    """
    Test AgentMail API by sending a test email
    """
    try:
        success = await agentmail_service.send_email(
            to_email=email,
            subject="Demo Hunters Test Email",
            body="""
            <h2>Test Email from Demo Hunters</h2>
            <p>This is a test email to verify AgentMail integration.</p>
            <p>If you received this, the integration is working!</p>
            """
        )
        
        if success:
            return TestResponse(
                success=True,
                message=f"Test email sent to {email}",
                data={"email": email}
            )
        else:
            return TestResponse(
                success=False,
                message="Failed to send email",
                data={}
            )
    except Exception as e:
        logger.error(f"Test AgentMail error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=TestResponse)
async def test_status():
    """
    Check test configuration status
    """
    from utils.config import settings
    
    return TestResponse(
        success=True,
        message="Test configuration",
        data={
            "mock_recording": settings.use_mock_recording,
            "recording_api": settings.recording_api_url,
            "klap_configured": bool(settings.klap_api_key),
            "agentmail_configured": bool(settings.agentmail_api_key),
            "supabase_configured": bool(settings.supabase_url)
        }
    )