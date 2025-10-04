"""RQ task functions for Helios worker."""

import os
import shutil
import subprocess
import uuid
from typing import Dict, Any

import docker
import redis
from rq import get_current_job

from app.core.config import get_settings
from app.core.constants import DockerSettings, TaskStatus, TaskSignals, RedisChannels


def run_task_in_docker(task_info: Dict[str, Any]) -> None:
    """Execute task in Docker container with proper logging and cleanup."""
    
    job = get_current_job()
    settings = get_settings()
    
    # Extract task information
    task_id = task_info["task_id"]
    task_path = task_info["task_path"]
    entrypoint = task_info["entrypoint"]
    resources = task_info.get("resources", {})
    
    # Initialize Redis client
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True
    )
    
    try:
        # Update task status to running
        redis_client.set(f"task:{task_id}:status", TaskStatus.RUNNING)
        
        # Initialize Docker client
        docker_client = docker.from_env()
        
        # Build Docker command
        docker_cmd = [
            "sh", "-c",
            f"pip install -r requirements.txt && python -u {entrypoint}"
        ]
        
        # Prepare Docker run parameters
        docker_params = {
            "image": "python:3.9-slim",
            "command": docker_cmd,
            "volumes": {task_path: {"bind": DockerSettings.MOUNT_POINT, "mode": "rw"}},
            "working_dir": DockerSettings.MOUNT_POINT,
            "remove": DockerSettings.AUTO_REMOVE,
            "detach": False,
            "stdout": True,
            "stderr": True,
            "stream": True
        }
        
        # Add resource limits if specified
        if resources.get("cpu"):
            docker_params["mem_limit"] = f"{resources['cpu']}g"
        
        if resources.get("mem"):
            docker_params["mem_limit"] = resources["mem"]
        
        # Create and start container
        print(f"Starting Docker container for task {task_id}")
        container = docker_client.containers.run(**docker_params)
        
        # Stream logs and publish to Redis
        for log_line in container.logs(stream=True):
            log_text = log_line.decode("utf-8", errors="ignore").rstrip()
            if log_text:
                redis_client.publish(f"{RedisChannels.LOGS_PREFIX}{task_id}", log_text)
        
        # Wait for container to finish and get exit code
        result = docker_client.containers.get(container.id).wait()
        exit_code = result["StatusCode"]
        
        # Publish completion signal
        if exit_code == 0:
            redis_client.set(f"task:{task_id}:status", TaskStatus.SUCCEEDED)
            redis_client.publish(f"{RedisChannels.LOGS_PREFIX}{task_id}", TaskSignals.COMPLETE)
        else:
            redis_client.set(f"task:{task_id}:status", TaskStatus.FAILED)
            redis_client.publish(
                f"{RedisChannels.LOGS_PREFIX}{task_id}",
                f"{TaskSignals.FAILED_PREFIX}:{exit_code}]"
            )
        
        print(f"Task {task_id} completed with exit code {exit_code}")
        
    except docker.errors.DockerException as e:
        error_msg = f"Docker error: {str(e)}"
        print(f"Task {task_id} failed: {error_msg}")
        
        redis_client.set(f"task:{task_id}:status", TaskStatus.FAILED)
        redis_client.publish(f"{RedisChannels.LOGS_PREFIX}{task_id}", f"{TaskSignals.FAILED_PREFIX}:Docker error]")
        redis_client.publish(f"{RedisChannels.LOGS_PREFIX}{task_id}", error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Task {task_id} failed: {error_msg}")
        
        redis_client.set(f"task:{task_id}:status", TaskStatus.FAILED)
        redis_client.publish(f"{RedisChannels.LOGS_PREFIX}{task_id}", f"{TaskSignals.FAILED_PREFIX}:Runtime error]")
        redis_client.publish(f"{RedisChannels.LOGS_PREFIX}{task_id}", error_msg)
        
    finally:
        # Cleanup: remove task directory
        try:
            if os.path.exists(task_path):
                shutil.rmtree(task_path)
                print(f"Cleaned up task directory: {task_path}")
        except Exception as e:
            print(f"Failed to clean up task directory {task_path}: {e}")
        
        # Close Redis connection
        try:
            redis_client.close()
        except:
            pass