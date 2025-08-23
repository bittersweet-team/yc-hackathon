import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from utils.supabase_client import get_supabase_client
from services.video_generator import video_generator

logger = logging.getLogger(__name__)

class TaskWorker:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.running = False
        
    async def start(self):
        """Start the task worker"""
        self.running = True
        logger.info("Task worker started")
        
        while self.running:
            try:
                # Try to claim a task
                task = await self.claim_next_task()
                
                if task:
                    await self.process_task(task)
                else:
                    # No tasks available, wait a bit
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"Task worker error: {str(e)}")
                await asyncio.sleep(10)
    
    async def stop(self):
        """Stop the task worker"""
        self.running = False
        logger.info("Task worker stopped")
    
    async def claim_next_task(self) -> Optional[Dict[str, Any]]:
        """Claim the next available task from the queue"""
        try:
            response = self.supabase.rpc('claim_next_task').execute()
            
            # Check if we got a valid task (not just a row with NULL id)
            if response.data and response.data.get('id'):
                return response.data
            return None
            
        except Exception as e:
            # Log the error but don't crash - this might be a transient issue
            error_msg = str(e)
            if "22P02" in error_msg or "invalid input syntax" in error_msg:
                # This is the UUID error, which means no tasks are available
                logger.debug("No tasks available in queue")
            else:
                logger.error(f"Failed to claim task: {error_msg}")
            return None
    
    async def process_task(self, task: Dict[str, Any]):
        """Process a claimed task"""
        task_id = task['id']
        task_type = task['task_type']
        payload = task['payload']
        
        logger.info(f"Processing task {task_id} of type {task_type}")
        
        try:
            if task_type == 'process_demo':
                await self.process_demo_task(payload)
            else:
                logger.error(f"Unknown task type: {task_type}")
                await self.mark_task_failed(task_id, f"Unknown task type: {task_type}")
                return
            
            # Mark task as completed
            await self.mark_task_completed(task_id)
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            await self.mark_task_failed(task_id, str(e))
    
    async def process_demo_task(self, payload: Dict[str, Any]):
        """Process a demo video generation task"""
        demo_id = payload.get('demo_id')
        user_email = payload.get('user_email')
        
        if not demo_id or not user_email:
            raise ValueError("Missing demo_id or user_email in payload")
        
        await video_generator.process_demo(demo_id, user_email)
    
    async def mark_task_completed(self, task_id: str):
        """Mark a task as completed"""
        self.supabase.table('task_queue').update({
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        }).eq('id', task_id).execute()
    
    async def mark_task_failed(self, task_id: str, error_message: str):
        """Mark a task as failed"""
        self.supabase.table('task_queue').update({
            'status': 'failed',
            'error_message': error_message,
            'completed_at': datetime.utcnow().isoformat()
        }).eq('id', task_id).execute()
    
    async def add_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        """Add a new task to the queue"""
        response = self.supabase.table('task_queue').insert({
            'task_type': task_type,
            'payload': payload,
            'status': 'pending'
        }).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['id']
        raise Exception("Failed to add task to queue")

# Global worker instance
task_worker = TaskWorker()

async def run_worker():
    """Run the task worker"""
    await task_worker.start()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(run_worker())