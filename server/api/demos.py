from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.demo import DemoRequest, DemoResponse, DemoStatus
from utils.auth import get_current_user
from utils.supabase_client import get_supabase_client
from workers.task_worker import task_worker
import uuid
from datetime import datetime

router = APIRouter(prefix="/api", tags=["demos"])

@router.post("/demo", response_model=DemoResponse)
async def create_demo(
    demo_request: DemoRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a new demo request
    """
    supabase = get_supabase_client()
    
    # Create demo record
    demo_data = {
        "user_id": current_user["id"],
        "product_url": str(demo_request.product_url),
        "description": demo_request.description or "",
        "status": DemoStatus.PENDING.value,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        response = supabase.table("demos").insert(demo_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create demo")
        
        demo = response.data[0]
        
        # Get user email (either from request or user profile)
        user_email = demo_request.email or current_user.get("email")
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Email is required for delivery")
        
        # Add task to database queue
        task_payload = {
            "demo_id": demo["id"],
            "user_email": user_email
        }
        
        await task_worker.add_task("process_demo", task_payload)
        
        return DemoResponse(**demo)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demos", response_model=List[DemoResponse])
async def list_demos(
    current_user: dict = Depends(get_current_user)
):
    """
    List all demos for the current user
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("demos")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .order("created_at", desc=True)\
            .execute()
        
        if response.data:
            return [DemoResponse(**demo) for demo in response.data]
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo/{demo_id}", response_model=DemoResponse)
async def get_demo(
    demo_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get demo status and details
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("demos")\
            .select("*")\
            .eq("id", demo_id)\
            .eq("user_id", current_user["id"])\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Demo not found")
        
        return DemoResponse(**response.data)
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Demo not found")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/demo/{demo_id}")
async def delete_demo(
    demo_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a demo
    """
    supabase = get_supabase_client()
    
    try:
        # Check if demo exists and belongs to user
        check_response = supabase.table("demos")\
            .select("id")\
            .eq("id", demo_id)\
            .eq("user_id", current_user["id"])\
            .single()\
            .execute()
        
        if not check_response.data:
            raise HTTPException(status_code=404, detail="Demo not found")
        
        # Delete the demo
        supabase.table("demos")\
            .delete()\
            .eq("id", demo_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        return {"message": "Demo deleted successfully"}
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Demo not found")
        raise HTTPException(status_code=500, detail=str(e))