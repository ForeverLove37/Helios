"""FastAPI application for Helios Manager."""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.api.tasks import router as tasks_router
from app.core.config import get_settings
from app.websocket.manager import websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Helios Manager starting up...")
    
    # Create task storage directory if it doesn't exist
    import os
    os.makedirs(settings.task_storage_path, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Helios Manager shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Helios Manager",
    description="一键式远程计算平台管理服务",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])

# Add WebSocket route
app.websocket("/ws/logs/{task_id}")(websocket_endpoint)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Helios Manager is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "helios-manager"}


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )