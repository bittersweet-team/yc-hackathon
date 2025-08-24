from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from api.demos import router as demos_router
from api.test import router as test_router
from utils.config import settings
from utils.supabase_client import get_supabase_client
from workers.task_worker import task_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background task for worker
worker_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_task
    # Startup
    logger.info("Starting Demo Hunters Backend...")
    
    # Start task worker in background
    worker_task = asyncio.create_task(task_worker.start())
    logger.info("Task worker started in background")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Demo Hunters Backend...")
    
    # Stop task worker
    if worker_task:
        await task_worker.stop()
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

# Create FastAPI app
app = FastAPI(
    title="Demo Hunters API",
    description="AI-powered demo video generation service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(demos_router)
app.include_router(test_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    supabase = get_supabase_client()
    
    # Check task queue status
    try:
        queue_status = supabase.table("task_queue").select("status").execute()
        pending_tasks = len([t for t in queue_status.data if t['status'] == 'pending'])
        processing_tasks = len([t for t in queue_status.data if t['status'] == 'processing'])
    except:
        pending_tasks = 0
        processing_tasks = 0
    
    return {
        "status": "healthy",
        "service": "Demo Hunters Backend",
        "version": "1.0.0",
        "task_queue": {
            "pending": pending_tasks,
            "processing": processing_tasks,
            "worker_running": worker_task is not None and not worker_task.done()
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Demo Hunters API",
        "documentation": "/docs",
        "health": "/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level="info"
    )