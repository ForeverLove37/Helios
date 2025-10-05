"""Task submission API endpoints."""

import json
import os
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Dict

import redis
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from rq import Queue

from app.api.models import TaskInfo, TaskMetadata, TaskSubmissionResponse, TaskStatusResponse
from app.core.config import get_settings
from app.core.constants import QueueNames, TaskStatus, TaskPriority
from app.core.redis import get_redis_client

router = APIRouter()


@router.post("/submit", response_model=TaskSubmissionResponse)
async def submit_task(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> TaskSubmissionResponse:
    """Submit a new task for execution."""
    
    settings = get_settings()
    
    try:
        # Parse metadata
        metadata_dict = json.loads(metadata)
        task_metadata = TaskMetadata(**metadata_dict)
        
        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only .zip files are allowed")
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Create task directory
        task_dir = Path(settings.task_storage_path) / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded zip file
        zip_path = task_dir / "project.zip"
        with open(zip_path, "wb") as zip_file:
            shutil.copyfileobj(file.file, zip_file)
        
        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(task_dir)
        
        # Remove zip file after extraction
        zip_path.unlink()
        
        # Create task info
        task_info = TaskInfo(
            task_id=task_id,
            task_path=str(task_dir),
            entrypoint=task_metadata.entrypoint,
            priority=task_metadata.priority,
            name=task_metadata.name,
            resources=task_metadata.resources
        )
        
        # Initialize task status in Redis
        redis_client.set(f"task:{task_id}:status", TaskStatus.PENDING)
        
        # Enqueue task to appropriate priority queue
        queue_name = QueueNames.HIGH if task_metadata.priority == TaskPriority.HIGH else QueueNames.DEFAULT
        queue = Queue(queue_name, connection=redis_client)
        queue.enqueue(
            "app.worker.tasks.run_task_in_docker",
            task_info.dict(),
            job_id=task_id,
            job_timeout=settings.docker_timeout
        )
        
        return TaskSubmissionResponse(
            success=True,
            task_id=task_id,
            message="Task submitted successfully."
        )
        
    except Exception as e:
        # Clean up on error
        if 'task_dir' in locals() and task_dir.exists():
            shutil.rmtree(task_dir)
        
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    redis_client: redis.Redis = Depends(get_redis_client)
) -> TaskStatusResponse:
    """Get task status."""
    
    status = redis_client.get(f"task:{task_id}:status")
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status
    )