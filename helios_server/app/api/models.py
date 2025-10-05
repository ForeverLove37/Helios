"""Data models for Helios API."""

import uuid
from typing import Dict, Optional

from pydantic import BaseModel, Field


class TaskMetadata(BaseModel):
    """Task metadata model."""
    entrypoint: str = Field(..., description="Entry script filename")
    priority: str = Field("default", description="Task priority")
    name: str = Field(..., description="Human-readable task name")
    resources: Dict[str, str] = Field(default_factory=dict, description="Resource limits")


class TaskSubmissionRequest(BaseModel):
    """Task submission request model."""
    metadata: TaskMetadata


class TaskSubmissionResponse(BaseModel):
    """Task submission response model."""
    success: bool
    task_id: str
    message: str


class TaskInfo(BaseModel):
    """Task information model."""
    task_id: str
    task_path: str
    entrypoint: str
    priority: str
    name: str
    resources: Dict[str, str]


class TaskStatusResponse(BaseModel):
    """Task status response model."""
    task_id: str
    status: str